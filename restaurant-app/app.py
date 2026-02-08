"""
Restaurant Management Web Application
LAN-based system with Blue Team Security Features
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import sqlite3
import re
import os
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'  # Change this in production

# Database configuration
DATABASE = 'restaurant.db'

# Lab Mode Configuration - Set to True only for authorized training/labs
LAB_MODE = True  # Set to True to enable SQL injection vulnerability for training

# Configure logging
if not os.path.exists('logs'):
    os.makedirs('logs')

# Access log for normal operations
access_logger = logging.getLogger('access')
access_logger.setLevel(logging.INFO)
access_handler = RotatingFileHandler('logs/access.log', maxBytes=10000000, backupCount=5)
access_handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(message)s'
))
access_logger.addHandler(access_handler)

# Security alert log for suspicious activity
alert_logger = logging.getLogger('security')
alert_logger.setLevel(logging.WARNING)
alert_handler = RotatingFileHandler('logs/security_alerts.log', maxBytes=10000000, backupCount=5)
alert_handler.setFormatter(logging.Formatter(
    '%(asctime)s - ALERT - %(message)s'
))
alert_logger.addHandler(alert_handler)

# Database helper functions
def get_db():
    """Create database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Orders table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            item TEXT NOT NULL,
            quantity INTEGER DEFAULT 1,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')
    
    # Hidden secret coupons table (trap for SQL injection exploiters)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS secret_coupons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coupon_code TEXT UNIQUE NOT NULL,
            discount_percentage INTEGER DEFAULT 50,
            is_trap INTEGER DEFAULT 1,
            claimed_by TEXT,
            claimed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert trap coupons - ALL COUPONS ARE TRAPS
    # These look legitimate but all trigger exploit detection
    trap_coupons = [
        ('SMASH_BURGERS', 99, 1),
        ('SUMMER2025', 50, 1),
        ('WELCOME50', 50, 1),
        ('DISCOUNT25', 25, 1),
        ('PROMO_OFFER', 35, 1),
        ('FLAT_OFF_40', 40, 1),
        ('EXCLUSIVE_99', 99, 1),
        ('SAVE_NOW', 30, 1),
        ('COUPON_HACK', 60, 1),
        ('SECRET_CODE', 75, 1),
    ]
    
    for coupon_code, discount, is_trap in trap_coupons:
        cursor.execute("SELECT * FROM secret_coupons WHERE coupon_code = ?", (coupon_code,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO secret_coupons (coupon_code, discount_percentage, is_trap, created_at) VALUES (?, ?, ?, ?)",
                (coupon_code, discount, is_trap, datetime.now())
            )
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("⚠️  NO DEFAULT ADMIN ACCOUNT CREATED")
    print("="*60)
    print("You must create an admin account via registration.")
    print("After registering, manually set role to 'admin' in database.")
    print("SQL: UPDATE users SET role='admin' WHERE username='your_username';")
    print("="*60 + "\n")

# Security validation functions
def is_valid_input(text, max_length=100):
    """Validate user input for security"""
    if not text or len(text) > max_length:
        return False
    
    # Check for common injection patterns
    suspicious_patterns = [
        r'<script',
        r'javascript:',
        r'onerror=',
        r'onload=',
        r'eval\(',
        r'exec\(',
        r'union\s+select',
        r'drop\s+table',
        r'insert\s+into',
        r'--\s*$',
        r'/\*.*\*/',
        r';\s*drop',
        r';\s*delete'
    ]
    
    for pattern in suspicious_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            alert_logger.warning(f"Suspicious input detected: {text[:50]} from IP: {request.remote_addr}")
            return False
    
    return True

def log_access(action, username=None, details=None):
    """Log normal access activity"""
    ip = request.remote_addr
    msg = f"IP: {ip} | Action: {action}"
    if username:
        msg += f" | User: {username}"
    if details:
        msg += f" | Details: {details}"
    access_logger.info(msg)

def log_alert(alert_type, details):
    """Log security alerts"""
    ip = request.remote_addr
    msg = f"Type: {alert_type} | IP: {ip} | Details: {details}"
    alert_logger.warning(msg)

def check_trap_coupon(coupon_code, username):
    """Check if a coupon is a trap for SQL injection exploiters"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT is_trap, claimed_by FROM secret_coupons WHERE coupon_code = ?",
        (coupon_code,)
    )
    result = cursor.fetchone()
    conn.close()
    
    if result and result['is_trap'] == 1:
        # This is a trap coupon - log the exploit attempt
        log_alert('SQLI_EXPLOITER', 
                 f'User {username} claimed trap coupon: {coupon_code} - Likely SQL injection exploitation')
        
        # Update coupon record to mark it as claimed
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE secret_coupons SET claimed_by = ?, claimed_at = ? WHERE coupon_code = ?",
            (username, datetime.now(), coupon_code)
        )
        conn.commit()
        conn.close()
        
        return True
    return False

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            log_alert('UNAUTHORIZED_ACCESS', f'Attempted to access {request.path} without login')
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            log_alert('UNAUTHORIZED_ACCESS', f'Attempted to access {request.path} without login')
            return redirect(url_for('login'))
        
        # Check if user is admin
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE username = ?", (session['username'],))
        user = cursor.fetchone()
        conn.close()
        
        if not user or user['role'] != 'admin':
            log_alert('PRIVILEGE_ESCALATION', f"User {session['username']} attempted to access admin area")
            flash('Unauthorized access. This incident has been logged.', 'error')
            return redirect(url_for('menu'))
        
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Home page redirects to menu"""
    return redirect(url_for('menu'))

@app.route('/menu')
def menu():
    """Display restaurant menu"""
    log_access('VIEW_MENU', session.get('username'))
    return render_template('menu.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validate input
        if not is_valid_input(username, 50):
            log_alert('INVALID_REGISTRATION', f'Invalid username pattern: {username[:50]}')
            flash('Invalid username. Please use only letters, numbers, and basic characters.', 'error')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html')
        
        # Check if username exists
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            flash('Username already exists. Please choose another.', 'error')
            return render_template('register.html')
        
        # Create new user
        hashed_password = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hashed_password, 'user')
        )
        conn.commit()
        conn.close()
        
        log_access('REGISTER', username, 'New user registered')
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validate input
        if not is_valid_input(username, 50):
            log_alert('INVALID_LOGIN', f'Invalid username pattern: {username[:50]}')
            flash('Invalid credentials.', 'error')
            return render_template('login.html')
        
        # Check credentials
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            session['role'] = user['role']
            log_access('LOGIN', username, f'Successful login - Role: {user["role"]}')
            
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('menu'))
        else:
            log_alert('FAILED_LOGIN', f'Failed login attempt for username: {username}')
            flash('Invalid username or password.', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/login-advanced', methods=['GET', 'POST'])
def login_advanced():
    """
    INTENTIONAL HARD SQL INJECTION VULNERABILITY IN LOGIN
    
    Hidden advanced login endpoint using vulnerable query construction.
    Allows authentication bypass via SQL injection.
    
    WARNING: This is deliberately vulnerable for training purposes ONLY
    Production login systems MUST use parameterized queries and proper password hashing!
    
    Attack vectors:
    - Username: admin' OR '1'='1' --
    - Username: admin' OR 1=1 --
    - Username: admin' --
    - Username: ' OR '1'='1
    - Password: Irrelevant (bypassed by SQL injection)
    """
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # NO input validation on advanced login
        # Direct string concatenation vulnerability
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # ========== INTENTIONAL HARD SQL INJECTION ==========
            # VULNERABLE: Username directly concatenated
            # This allows SQL injection to bypass authentication
            # An attacker can inject SQL to authenticate as ANY user
            # Even without knowing the password!
            
            if username:  # Only if username provided
                # UNSAFE: String concatenation with user input
                query = f"SELECT * FROM users WHERE username = '{username}' LIMIT 1"
                
                # Log the injection attempt
                log_access('LOGIN_ADVANCED_ATTEMPT', username, f'Query: {query[:50]}...')
                
                try:
                    cursor.execute(query)
                    user = cursor.fetchone()
                    
                    if user:
                        # DANGEROUS: If injection returned a user, log in regardless of password!
                        # Real system would check: check_password_hash(user['password'], password)
                        # But we don't, simulating a vulnerable system
                        
                        session['username'] = user['username']
                        session['role'] = user['role']
                        
                        # Log successful authentication
                        log_access('LOGIN_ADVANCED_SUCCESS', user['username'], f'Logged in via SQL injection')
                        
                        # Check if this was via SQL injection
                        if "'" in username or ";" in username or "--" in username or " OR " in username.upper():
                            log_alert('LOGIN_SQLI_EXPLOIT', 
                                     f'User {user["username"]} authentication via SQL injection | Payload: {username[:100]}')
                        
                        if user['role'] == 'admin':
                            return redirect(url_for('admin_dashboard'))
                        return redirect(url_for('menu'))
                    else:
                        log_alert('LOGIN_ADVANCED_FAILED', f'Failed login attempt: {username[:50]}')
                        flash('Invalid credentials.', 'error')
                        
                except Exception as e:
                    # Log SQL errors - indicates injection attempt
                    error_msg = str(e)[:100]
                    log_alert('LOGIN_ADVANCED_ERROR', 
                             f'SQL error in advanced login: {error_msg} | Username: {username[:50]}')
                    flash('Error processing login. This incident has been logged.', 'error')
                finally:
                    conn.close()
            
        except Exception as e:
            log_alert('LOGIN_ADVANCED_EXCEPTION', f'Unexpected error: {str(e)[:50]}')
            flash('Unexpected error. Please try again.', 'error')
    
    return render_template('login_advanced.html')

@app.route('/logout')
def logout():
    """User logout"""
    username = session.get('username')
    log_access('LOGOUT', username)
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('menu'))

@app.route('/order', methods=['POST'])
@login_required
def place_order():
    """Place a food order"""
    item = request.form.get('item', '').strip()
    quantity = request.form.get('quantity', '1')
    
    # Validate input
    if not is_valid_input(item, 100):
        log_alert('INVALID_ORDER', f'Suspicious order input from {session["username"]}: {item[:50]}')
        flash('Invalid order. Please try again.', 'error')
        return redirect(url_for('menu'))
    
    try:
        quantity = int(quantity)
        if quantity < 1 or quantity > 99:
            raise ValueError()
    except ValueError:
        flash('Invalid quantity.', 'error')
        return redirect(url_for('menu'))
    
    # Save order
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO orders (username, item, quantity, status) VALUES (?, ?, ?, ?)",
        (session['username'], item, quantity, 'pending')
    )
    conn.commit()
    conn.close()
    
    log_access('ORDER_PLACED', session['username'], f'Item: {item}, Qty: {quantity}')
    flash(f'Order placed successfully: {quantity}x {item}', 'success')
    return redirect(url_for('menu'))

@app.route('/my-orders')
@login_required
def my_orders():
    """View user's own orders"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM orders WHERE username = ? ORDER BY created_at DESC",
        (session['username'],)
    )
    orders = cursor.fetchall()
    conn.close()
    
    log_access('VIEW_MY_ORDERS', session['username'])
    return render_template('my_orders.html', orders=orders)

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    log_access('VIEW_ADMIN_DASHBOARD', session['username'])
    return render_template('admin_dashboard.html')

@app.route('/admin/orders')
@admin_required
def admin_orders():
    """View all orders (admin only)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders ORDER BY created_at DESC LIMIT 100")
    orders = cursor.fetchall()
    conn.close()
    
    log_access('VIEW_ALL_ORDERS', session['username'])
    return render_template('admin_orders.html', orders=orders)

@app.route('/admin/orders/search', methods=['GET', 'POST'])
@admin_required
def admin_orders_search():
    """
    INTENTIONAL HARD SQL INJECTION VULNERABILITY
    
    Advanced SQL injection vulnerability in admin search functionality.
    This is hidden from UI and requires knowledge of endpoint to exploit.
    
    HARD MODE: String concatenation in WHERE clause with user input
    Vulnerable to: UNION-based injection, boolean-based blind injection, time-based blind injection
    
    WARNING: This is deliberately vulnerable for training purposes ONLY
    Production code must NEVER use this pattern!
    """
    
    search_term = request.args.get('q', '').strip()
    orders = []
    
    if search_term:
        log_access('ADMIN_SEARCH', session['username'], f'Search: {search_term}')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # ========== INTENTIONAL HARD SQL INJECTION ==========
            # String concatenation directly in WHERE clause
            # Attacker can break query and execute arbitrary SQL
            # 
            # Example payloads:
            # q=" OR 1=1 --
            # q=" UNION SELECT id,username,item,4,5,6 FROM users --
            # q=" AND 1=2 UNION SELECT id,username,item,status,created_at,4 FROM secret_coupons --
            
            query = f"SELECT * FROM orders WHERE item LIKE '%{search_term}%' OR username LIKE '%{search_term}%'"
            cursor.execute(query)
            orders = cursor.fetchall()
            conn.close()
            
            # Check if results contain trap data
            for order in orders:
                if order['item'] == 'TRAP_SQLI_EXPLOIT' or order['username'] == 'trap_user':
                    log_alert('SQLI_EXPLOITER', 
                             f'User {session["username"]} exploited hard SQL injection in /admin/orders/search | Payload: {search_term[:100]}')
            
        except Exception as e:
            # Log the error - indicates successful SQL injection exploitation
            error_msg = str(e)[:100]
            log_alert('HARD_SQLI_ERROR', 
                     f'SQL error in admin search from {session["username"]}: {error_msg} | Payload: {search_term[:50]}')
            orders = []
    
    log_access('ADMIN_ORDERS_SEARCH', session['username'])
    return render_template('admin_orders_search.html', orders=orders, search_term=search_term)

@app.route('/admin/logs')
@admin_required
def admin_logs():
    """View security logs (admin only)"""
    # Read last 100 lines from security alerts
    alerts = []
    try:
        with open('logs/security_alerts.log', 'r') as f:
            alerts = f.readlines()[-100:]
            alerts.reverse()
    except FileNotFoundError:
        alerts = ['No security alerts yet.']
    
    log_access('VIEW_SECURITY_LOGS', session['username'])
    return render_template('admin_logs.html', alerts=alerts)

@app.route('/admin/exploiters')
@admin_required
def admin_exploiters():
    """View detected SQL injection exploiters (admin only)"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT coupon_code, claimed_by, claimed_at FROM secret_coupons WHERE is_trap = 1 AND claimed_by IS NOT NULL"
    )
    exploiters = cursor.fetchall()
    conn.close()
    
    log_access('VIEW_EXPLOITER_LOGS', session['username'])
    return render_template('admin_exploiters.html', exploiters=exploiters)

@app.route('/admin/update-order/<int:order_id>', methods=['POST'])
@admin_required
def update_order_status(order_id):
    """Update order status (admin only)"""
    new_status = request.form.get('status', 'pending')
    
    if new_status not in ['pending', 'preparing', 'completed', 'cancelled']:
        flash('Invalid status.', 'error')
        return redirect(url_for('admin_orders'))
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE orders SET status = ? WHERE id = ?",
        (new_status, order_id)
    )
    conn.commit()
    conn.close()
    
    log_access('UPDATE_ORDER', session['username'], f'Order {order_id} set to {new_status}')
    flash(f'Order #{order_id} updated to {new_status}.', 'success')
    return redirect(url_for('admin_orders'))

@app.route('/lab/billing', methods=['GET', 'POST'])
@login_required
def lab_billing():
    """
    LAB MODE ONLY - Vulnerable billing/coupon endpoint for training purposes
    
    INTENTIONAL SQL INJECTION VULNERABILITY - Used for cybersecurity training
    Only active when LAB_MODE = True in configuration
    
    This endpoint demonstrates how unsanitized user input can be exploited.
    Production systems should NEVER use this pattern!
    """
    
    if not LAB_MODE:
        log_alert('LAB_MODE_DISABLED', f'Unauthorized access to lab endpoint from {session.get("username")}')
        return redirect(url_for('menu')), 403
    
    if request.method == 'POST':
        coupon_code = request.form.get('coupon_code', '').strip()
        
        if not coupon_code:
            flash('Please enter a coupon code.', 'error')
            return render_template('lab_billing.html')
        
        log_access('LAB_BILLING_ATTEMPT', session['username'], f'Coupon: {coupon_code}')
        
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # ========== INTENTIONAL VULNERABILITY FOR TRAINING ==========
            # THIS IS DELIBERATELY UNSAFE - Shows SQL injection exploitation
            # NEVER use string concatenation for queries in production!
            # 
            # An attacker can inject SQL like:
            # coupon_code: ' OR '1'='1
            # coupon_code: '; DROP TABLE orders; --
            # coupon_code: ' UNION SELECT * FROM secret_coupons WHERE '1'='1
            
            if LAB_MODE:
                # VULNERABLE: Using string concatenation (SQL injection possible)
                query = f"SELECT * FROM secret_coupons WHERE coupon_code = '{coupon_code}'"
                cursor.execute(query)
            else:
                # SAFE: Using parameterized query
                cursor.execute("SELECT * FROM secret_coupons WHERE coupon_code = ?", (coupon_code,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                discount = result['discount_percentage']
                
                # Check if this is a trap coupon (indicates exploitation)
                is_trap = check_trap_coupon(coupon_code, session['username'])
                
                if is_trap:
                    flash(f'⚠️ SECURITY ALERT: Trap coupon detected! This incident has been logged.',
                          'warning')
                else:
                    flash(f'Coupon applied! {discount}% discount', 'success')
                
                return render_template('lab_billing.html', 
                                     coupon_found=True, 
                                     discount=discount,
                                     is_trap=is_trap)
            else:
                flash('Coupon not found.', 'error')
                return render_template('lab_billing.html')
                
        except Exception as e:
            # Log the error - may indicate successful SQL injection attack
            error_msg = str(e)[:100]
            log_alert('LAB_BILLING_ERROR', 
                     f'Error from {session["username"]}: {error_msg} | Coupon input: {coupon_code[:50]}')
            flash('Error processing coupon. Error logged for security review.', 'error')
            return render_template('lab_billing.html')
    
    return render_template('lab_billing.html')
@app.errorhandler(404)
def page_not_found(e):
    log_alert('404_ERROR', f'Page not found: {request.path}')
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    log_alert('500_ERROR', f'Internal error on: {request.path}')
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    print("=" * 60)
    print("Restaurant Management System - Starting...")
    print("=" * 60)
    print("Default Admin Credentials:")
    print("  Username: admin")
    print("  Password: admin123")
    print("  ** CHANGE THIS IN PRODUCTION **")
    print("=" * 60)
    print("Server will be accessible from any device on the LAN")
    print("Access via: http://<your-local-ip>:5000")
    print("=" * 60)
    
    # Run on all interfaces (0.0.0.0) to allow LAN access
    app.run(host='0.0.0.0', port=5000, debug=True)
