# Quick Start Guide
## Restaurant Management System - Get Running in 5 Minutes

### Step 1: Install Dependencies (30 seconds)
```bash
pip install flask werkzeug
```

### Step 2: Start the Server (10 seconds)
```bash
python app.py
```

### Step 3: Find Your IP Address

**Windows:**
```cmd
ipconfig
```

**Mac/Linux:**
```bash
ifconfig
```

Look for your IPv4 address (e.g., 192.168.1.100)

### Step 4: Access the Application

On any device on the same network, open:
```
http://YOUR-IP-ADDRESS:5000
```

Example: `http://192.168.1.100:5000`

### Default Admin Login
- **Username:** admin
- **Password:** admin123

### Quick Test

1. **Create a user account:**
   - Click "Register"
   - Username: testuser
   - Password: test123
   - Click "Register"

2. **Place an order:**
   - Login with testuser
   - Click "Order" on any menu item
   - See confirmation

3. **View as admin:**
   - Logout
   - Login as admin
   - Go to "Admin Dashboard"
   - Click "View Orders"
   - See testuser's order

4. **Test security:**
   - Try login with: `admin' OR '1'='1`
   - Login will fail
   - Login as admin
   - Go to "Security Logs"
   - See the detected attack!

### That's it! You're ready to demonstrate.

---

## Troubleshooting

**Can't access from other devices?**
- Check firewall (allow port 5000)
- Verify same WiFi network
- Try: `http://localhost:5000` on host machine first

**Port 5000 in use?**
- Change port in app.py (line 337): `app.run(host='0.0.0.0', port=5001)`

**Need help?**
- See full README.md for detailed instructions
- Check logs/ folder for error details

---

## Quick Demo Script

**30-Second Demo:**
1. Show menu page
2. Place an order as user
3. Show admin dashboard
4. Show security logs

**2-Minute Demo:**
1. Register new user
2. Place multiple orders
3. Login as admin
4. Update order status
5. Attempt SQL injection
6. Show detected attack in logs

**5-Minute Demo:**
1. Full user workflow
2. Admin order management
3. Security feature walkthrough
4. Live attack demonstration
5. Log analysis explanation

---

**Ready to impress? Start the server and go! **
