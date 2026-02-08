# Restaurant Management Web Application
## LAN-Based System with Blue Team Security Features

A comprehensive web application demonstrating real-world restaurant management functionality combined with cybersecurity blue-team principles.

---

##  Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Technology Stack](#technology-stack)
4. [Installation](#installation)
5. [Deployment on LAN](#deployment-on-lan)
6. [Security Features](#security-features)
7. [User Guide](#user-guide)
8. [Admin Guide](#admin-guide)
9. [Architecture](#architecture)
10. [Testing Attack Scenarios](#testing-attack-scenarios)
11. [Troubleshooting](#troubleshooting)

---

##  Overview

This project is a dual-purpose web application:

**Functional Purpose:**
- Simulate a real restaurant website
- Allow customers to browse menu and place orders
- Enable administrators to manage orders and monitor operations

**Security Purpose:**
- Demonstrate blue team cybersecurity practices
- Detect and log malicious behavior
- Monitor suspicious activity in real-time
- Respond to attacks with appropriate alerts

The system runs entirely on a local area network (LAN), making it perfect for controlled demonstrations, education, and cyber-defense training.

---

##  Features

### Customer Features
-   User registration and authentication
-   Browse restaurant menu with categories
-   Place food orders with quantity selection
-   View personal order history
-   Track order status (pending, preparing, completed, cancelled)

### Admin Features
-   Secure admin dashboard
-   View all customer orders
-   Update order status
-   Monitor security alerts in real-time
-   Review access logs and suspicious activity
-   Role-based access control

### Security Features (Blue Team)
-   Input validation against injection attacks
-   Failed login attempt detection
-   Unauthorized access monitoring
-   Privilege escalation detection
-   Comprehensive activity logging
-   Real-time alert generation
-   Separate logs for access and security events

---

##  Technology Stack

- **Backend:** Flask (Python)
- **Database:** SQLite
- **Frontend:** HTML5, CSS3, Jinja2 Templates
- **Security:** Werkzeug (password hashing), custom validation
- **Logging:** Python logging module with rotating file handlers

---

##  Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Step 1: Install Python Dependencies

```bash
pip install flask werkzeug
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

### Step 2: Verify Installation

```bash
python --version
# Should show Python 3.8 or higher

python -c "import flask; print(flask.__version__)"
# Should show Flask version (e.g., 3.0.0)
```

---

##  Deployment on LAN

### Step 1: Find Your Local IP Address

**On Windows:**
```cmd
ipconfig
```
Look for "IPv4 Address" under your active network adapter (e.g., 192.168.1.100)

**On Linux/Mac:**
```bash
ifconfig
# or
ip addr show
```
Look for "inet" under your active interface (e.g., 192.168.1.100)

### Step 2: Configure Firewall

**Windows Firewall:**
1. Open "Windows Defender Firewall"
2. Click "Allow an app through firewall"
3. Allow Python on Private networks
4. Or create an inbound rule for port 5000

**Linux (UFW):**
```bash
sudo ufw allow 5000/tcp
```

### Step 3: Start the Application

```bash
python app.py
```

You should see:
```
============================================================
Restaurant Management System - Starting...
============================================================
Default Admin Credentials:
  Username: admin
  Password: admin123
  ** CHANGE THIS IN PRODUCTION **
============================================================
Server will be accessible from any device on the LAN
Access via: http://<your-local-ip>:5000
============================================================
```

### Step 4: Access from Other Devices

On any device connected to the same network:

1. Open a web browser
2. Navigate to: `http://<your-local-ip>:5000`
   - Example: `http://192.168.1.100:5000`
3. You should see the restaurant menu page

---

##  Security Features

### 1. Input Validation

The system checks all user inputs for malicious patterns:
- SQL injection attempts (`UNION SELECT`, `DROP TABLE`)
- Cross-Site Scripting (XSS) (`<script>`, `onerror=`)
- Command injection attempts
- Path traversal attempts

**Example Detection:**
```python
# User tries: username = "admin' OR '1'='1"
# System detects SQL injection pattern and logs alert
```

### 2. Authentication Monitoring

- Failed login attempts are logged with IP address
- Multiple failed attempts from same IP trigger alerts
- Successful logins are logged for audit trail

### 3. Access Control

- Role-based permissions (user vs admin)
- Unauthorized access attempts logged
- Privilege escalation attempts detected

### 4. Logging System

**Access Log** (`logs/access.log`):
- Normal operations
- Successful logins
- Order placements
- Page views

**Security Alert Log** (`logs/security_alerts.log`):
- Failed login attempts
- Suspicious input patterns
- Unauthorized access attempts
- Privilege escalation attempts

---

##  User Guide

### Registration

1. Click "Register" in the navigation bar
2. Choose a username (letters, numbers, underscore, hyphen only)
3. Create a password (minimum 6 characters)
4. Click "Register"

### Logging In

1. Click "Login" in the navigation bar
2. Enter your username and password
3. Click "Login"

### Placing an Order

1. Log in to your account
2. Browse the menu
3. Select quantity for desired item
4. Click "Order" button
5. Order confirmation will appear

### Viewing Your Orders

1. Click "My Orders" in the navigation
2. See all your orders with current status
3. Status options:
   - **Pending:** Order received, awaiting preparation
   - **Preparing:** Order is being prepared
   - **Completed:** Order is ready
   - **Cancelled:** Order was cancelled

---

##  Admin Guide

### Admin Login

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

 **Important:** Change the admin password immediately after first login!

### Admin Dashboard

After logging in as admin:

1. Click "Admin Dashboard"
2. Four main sections:
   - **Order Management:** View and update all orders
   - **Security Logs:** Monitor alerts and suspicious activity
   - **System Status:** View system health
   - **User Management:** (Coming soon)

### Managing Orders

1. Go to "Order Management"
2. View all customer orders in table format
3. To update order status:
   - Select new status from dropdown
   - Click "Update" button
4. Customer will see updated status in their order history

### Monitoring Security

1. Go to "Security Logs"
2. Review recent alerts including:
   - Failed login attempts
   - Malicious input detection
   - Unauthorized access attempts
3. Each alert shows:
   - Timestamp
   - Alert type
   - IP address
   - Details of the incident

---

##  Architecture

### Directory Structure

```
restaurant-app/
├── app.py                 # Main Flask application
├── restaurant.db          # SQLite database (created on first run)
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── logs/                 # Log files (created on first run)
│   ├── access.log       # Normal access log
│   └── security_alerts.log  # Security alerts
├── static/
│   └── css/
│       └── style.css    # Application stylesheet
└── templates/           # HTML templates
    ├── base.html        # Base template
    ├── menu.html        # Menu page
    ├── login.html       # Login page
    ├── register.html    # Registration page
    ├── my_orders.html   # User orders page
    ├── admin_dashboard.html  # Admin dashboard
    ├── admin_orders.html     # Order management
    ├── admin_logs.html       # Security logs
    ├── 404.html         # 404 error page
    └── 500.html         # 500 error page
```

### Database Schema

**Users Table:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Orders Table:**
```sql
CREATE TABLE orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    item TEXT NOT NULL,
    quantity INTEGER DEFAULT 1,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username)
);
```

### Request Flow

```
User Browser
    ↓
Flask Server (app.py)
    ↓
Input Validation & Security Checks
    ↓
Database Operation (SQLite)
    ↓
Logging (Access & Security)
    ↓
Response to User
```

---

##  Testing Attack Scenarios

### Test 1: SQL Injection

**Attempt:**
```
Username: admin' OR '1'='1
Password: anything
```

**Expected Result:**
- Login fails
- Security alert logged
- Message: "Invalid credentials"
- Log entry shows: "Suspicious input detected"

### Test 2: XSS Attack

**Attempt:**
```
Order Item: <script>alert('XSS')</script>
```

**Expected Result:**
- Order rejected
- Security alert logged
- Message: "Invalid order. Please try again."

### Test 3: Unauthorized Access

**Attempt:**
1. Log in as regular user
2. Try to access: `http://<ip>:5000/admin`

**Expected Result:**
- Access denied
- Redirect to menu
- Security alert logged
- Log shows privilege escalation attempt

### Test 4: Failed Login Attempts

**Attempt:**
Try logging in with wrong password 3 times

**Expected Result:**
- Each attempt logged separately
- Security alerts generated
- IP address recorded

### Viewing Test Results

1. Log in as admin
2. Go to "Security Logs"
3. Review all detected attacks
4. Check `logs/security_alerts.log` for full details

---

## Troubleshooting

### Problem: Can't access from other devices

**Solution:**
1. Verify firewall allows port 5000
2. Ensure devices are on same network
3. Check IP address is correct
4. Try disabling firewall temporarily for testing

### Problem: Port 5000 already in use

**Solution:**
```bash
# Find process using port 5000
# Windows:
netstat -ano | findstr :5000

# Linux/Mac:
lsof -i :5000

# Kill the process or change port in app.py:
app.run(host='0.0.0.0', port=5001, debug=True)
```

### Problem: Database errors

**Solution:**
1. Delete `restaurant.db` file
2. Restart application
3. Database will be recreated automatically

### Problem: Logs not appearing

**Solution:**
1. Check `logs/` directory exists
2. Verify write permissions
3. Check disk space

### Problem: CSS not loading

**Solution:**
1. Hard refresh browser (Ctrl+F5)
2. Clear browser cache
3. Check Flask console for 404 errors
4. Verify `static/css/style.css` exists

---

##  Demonstration Tips

### For Judges/Evaluators

1. **Show Normal Operation:**
   - Register a user
   - Place an order
   - Show order tracking

2. **Demonstrate Security:**
   - Attempt SQL injection
   - Show alert in security logs
   - Explain detection mechanism

3. **Show Admin Capabilities:**
   - Log in as admin
   - Manage orders
   - Review security dashboard

4. **Explain Blue Team Approach:**
   - Focus on detection, not exploitation
   - Highlight logging and monitoring
   - Discuss real-world applications

### Key Talking Points

- **Real-world simulation:** Mimics actual restaurant systems
- **Security-first design:** Built with defensive measures
- **Comprehensive logging:** Full audit trail
- **Educational value:** Teaches defensive cybersecurity
- **LAN deployment:** Safe, controlled environment

---

##  Future Enhancements

- [ ] Rate limiting for login attempts
- [ ] Email notifications for security alerts
- [ ] User profile management
- [ ] Advanced order analytics
- [ ] Payment integration (simulation)
- [ ] Multi-factor authentication
- [ ] Session timeout
- [ ] HTTPS support
- [ ] Intrusion detection system integration

---

##  License

This project is for educational and demonstration purposes.

---

##  Support

For questions or issues:
1. Check the Troubleshooting section
2. Review log files for errors
3. Verify all dependencies are installed

---

##  Educational Context

This application demonstrates:
- **Web Development:** Full-stack application with Flask
- **Database Design:** Relational database with proper schema
- **Security Practices:** Input validation, authentication, authorization
- **Blue Team Skills:** Monitoring, logging, incident detection
- **Network Deployment:** LAN-based application hosting

Perfect for:
- Cybersecurity education
- Web development learning
- Blue team training
- Security competitions
- Academic projects

---

**Version:** 1.0  
**Last Updated:** February 2025  
**Status:** Production-Ready for LAN Deployment
