# Security Features Documentation
## Blue Team Cybersecurity Implementation

---

## Overview

This document details the blue team security features implemented in the Restaurant Management System. These features focus on **detection, logging, and response** rather than exploitation prevention alone.

---

## 1. Input Validation System

### Purpose
Detect and block malicious input patterns before they reach the database or application logic.

### Implementation

**Location:** `app.py` - `is_valid_input()` function

**Detected Patterns:**
```python
suspicious_patterns = [
    r'<script',           # XSS: Script injection
    r'javascript:',       # XSS: JavaScript protocol
    r'onerror=',          # XSS: Event handler
    r'onload=',           # XSS: Event handler
    r'eval\(',            # Code injection
    r'exec\(',            # Code injection
    r'union\s+select',    # SQL injection
    r'drop\s+table',      # SQL injection
    r'insert\s+into',     # SQL injection
    r'--\s*$',            # SQL comment
    r'/\*.*\*/',          # SQL comment block
    r';\s*drop',          # SQL injection
    r';\s*delete'         # SQL injection
]
```

### What Gets Logged

**When triggered:**
- Alert type: "Suspicious input detected"
- IP address of attacker
- First 50 characters of malicious input
- Timestamp

**Log file:** `logs/security_alerts.log`

### Example Attack Detection

**Attack attempt:**
```
Username: admin' OR '1'='1
```

**System response:**
```
2025-02-04 14:23:15 - ALERT - Type: INVALID_LOGIN | IP: 192.168.1.105 | Details: Invalid username pattern: admin' OR '1'='1
```

**User sees:** "Invalid credentials."

---

## 2. Authentication Monitoring

### Purpose
Track and log all authentication attempts, both successful and failed.

### Successful Logins

**What gets logged:**
- Username
- IP address
- Role (user/admin)
- Timestamp

**Log entry example:**
```
2025-02-04 14:25:30 - IP: 192.168.1.100 | Action: LOGIN | User: john_doe | Details: Successful login - Role: user
```

### Failed Login Attempts

**What gets logged:**
- Username attempted
- IP address
- Timestamp
- Alert flag

**Alert entry example:**
```
2025-02-04 14:26:45 - ALERT - Type: FAILED_LOGIN | IP: 192.168.1.105 | Details: Failed login attempt for username: admin
```

### Attack Scenarios Detected

1. **Brute force attempts:** Multiple failed logins from same IP
2. **Credential stuffing:** Failed attempts with various usernames
3. **SQL injection in login:** Malicious patterns in username field

---

## 3. Access Control & Authorization

### Role-Based Access Control (RBAC)

**Two roles:**
- `user`: Regular customers
- `admin`: Restaurant administrators

### Protected Routes

**Admin-only routes:**
- `/admin` - Admin dashboard
- `/admin/orders` - Order management
- `/admin/logs` - Security logs
- `/admin/update-order/<id>` - Order status updates

**User authentication required:**
- `/order` - Place orders
- `/my-orders` - View personal orders

### Unauthorized Access Detection

**Scenario 1: Accessing admin area without login**

**What happens:**
- Redirect to login page
- Alert logged
- User sees: "Please log in to access this page"

**Log entry:**
```
2025-02-04 15:30:12 - ALERT - Type: UNAUTHORIZED_ACCESS | IP: 192.168.1.110 | Details: Attempted to access /admin without login
```

**Scenario 2: Regular user trying to access admin area**

**What happens:**
- Redirect to menu
- Alert logged as privilege escalation attempt
- User sees: "Unauthorized access. This incident has been logged."

**Log entry:**
```
2025-02-04 15:35:20 - ALERT - Type: PRIVILEGE_ESCALATION | IP: 192.168.1.100 | Details: User john_doe attempted to access admin area
```

---

## 4. Activity Logging

### Access Log (`logs/access.log`)

**Records normal operations:**
- Page views
- Successful logins
- Orders placed
- Admin actions

**Log format:**
```
TIMESTAMP - IP: ADDRESS | Action: ACTION_TYPE | User: USERNAME | Details: ADDITIONAL_INFO
```

**Example entries:**
```
2025-02-04 16:00:01 - IP: 192.168.1.100 | Action: VIEW_MENU | User: john_doe
2025-02-04 16:00:15 - IP: 192.168.1.100 | Action: ORDER_PLACED | User: john_doe | Details: Item: Margherita Pizza, Qty: 2
2025-02-04 16:01:30 - IP: 192.168.1.50 | Action: VIEW_ADMIN_DASHBOARD | User: admin
2025-02-04 16:02:00 - IP: 192.168.1.50 | Action: UPDATE_ORDER | User: admin | Details: Order 15 set to preparing
```

### Security Alert Log (`logs/security_alerts.log`)

**Records suspicious/malicious activity:**
- Failed login attempts
- Malicious input detection
- Unauthorized access attempts
- Privilege escalation attempts

**Log format:**
```
TIMESTAMP - ALERT - Type: ALERT_TYPE | IP: ADDRESS | Details: DESCRIPTION
```

---

## 5. Order Validation

### Purpose
Ensure order data integrity and detect manipulation attempts.

### Validations

**Item name validation:**
- Maximum 100 characters
- Checks for malicious patterns
- Alphanumeric and basic punctuation only

**Quantity validation:**
- Must be integer
- Range: 1-99
- Prevents negative numbers or excessive quantities

### Attack Detection

**Scenario: Malicious item name**

**Attack:**
```
Item: <script>alert('Hacked')</script>
```

**System response:**
- Order rejected
- Alert logged
- User sees: "Invalid order. Please try again."

**Log entry:**
```
2025-02-04 17:00:00 - ALERT - Type: INVALID_ORDER | IP: 192.168.1.105 | Details: Suspicious order input from user123: <script>alert('Hacked')</script>
```

---

## 6. Error Handling

### Custom Error Pages

**404 - Page Not Found**
- Custom page shown
- Attempted path logged
- Helps detect directory traversal attempts

**500 - Internal Server Error**
- Generic error shown to user
- Full error logged for admin review
- Prevents information disclosure

### Error Logging

**404 errors logged:**
```
2025-02-04 18:00:00 - ALERT - Type: 404_ERROR | IP: 192.168.1.105 | Details: Page not found: /../../../../etc/passwd
```

This helps detect:
- Directory traversal attempts
- Scanning for hidden pages
- Automated vulnerability scanners

---

## 7. Session Management

### Session Security

**Features:**
- Secure session cookies
- Session-based authentication
- Automatic session cleanup on logout
- Role stored in session for quick access control

### Session Hijacking Prevention

**Measures:**
- Secret key for session encryption
- HTTPOnly cookies (if HTTPS enabled)
- Session invalidation on logout

---

## 8. Password Security

### Password Storage

**Method:** Werkzeug's PBKDF2-based hashing

**Features:**
- Passwords never stored in plain text
- Salted hashing
- Computational cost makes brute force difficult

**Code:**
```python
# Storing password
hashed = generate_password_hash(password)

# Verifying password
check_password_hash(hashed, password)
```

### Password Requirements

**Minimum length:** 6 characters (can be increased)

**Best practices for production:**
- Require 12+ characters
- Mix of uppercase, lowercase, numbers, symbols
- Password strength meter
- Password history (prevent reuse)

---

## 9. Real-Time Monitoring

### Admin Security Dashboard

**Features:**
- Live view of security alerts
- Last 100 alerts displayed
- Chronological order (newest first)
- Color-coded severity

**Information shown:**
- Alert type
- Timestamp
- IP address
- Detailed description

### Use Cases

**Incident Response:**
1. Admin notices multiple failed logins
2. Identifies attacker IP
3. Can block IP at firewall level
4. Reviews full attack timeline

**Threat Hunting:**
1. Admin reviews logs proactively
2. Identifies patterns of suspicious behavior
3. Implements additional protections
4. Updates security policies

---

## 10. Attack Surface Reduction

### Minimal Information Disclosure

**What attackers DON'T see:**
- Database error messages
- Stack traces
- File paths
- Version information

**Generic error messages:**
- "Invalid credentials" (not "username not found")
- "Invalid order" (not "detected SQL injection")
- "Unauthorized access" (not "admin role required")

### Defense in Depth

**Multiple layers:**
1. Input validation
2. Parameterized database queries
3. Session management
4. Role-based access control
5. Activity logging
6. Error handling

---

## Testing the Security Features

### Test Plan

**Test 1: SQL Injection Detection**
```
1. Go to login page
2. Username: admin' OR '1'='1
3. Password: anything
4. Submit
5. Check: Login fails, alert logged
```

**Test 2: XSS Prevention**
```
1. Login as regular user
2. Try to order: <script>alert('XSS')</script>
3. Submit
4. Check: Order rejected, alert logged
```

**Test 3: Privilege Escalation**
```
1. Login as regular user
2. Navigate to: /admin
3. Check: Access denied, redirected, alert logged
```

**Test 4: Failed Login Monitoring**
```
1. Attempt login with wrong password 5 times
2. Login as admin
3. Go to Security Logs
4. Check: All 5 attempts logged with IP
```

**Test 5: Order Manipulation**
```
1. Login as user
2. Try order with negative quantity: -5
3. Submit
4. Check: Order rejected
```

---

## Log Analysis Guide

### Understanding Log Entries

**Normal Access Log Entry:**
```
2025-02-04 16:00:15 - IP: 192.168.1.100 | Action: ORDER_PLACED | User: john_doe | Details: Item: Pizza, Qty: 2
```

**Breakdown:**
- **Timestamp:** When action occurred
- **IP:** Source IP address
- **Action:** What happened
- **User:** Who did it
- **Details:** Additional context

**Security Alert Entry:**
```
2025-02-04 16:05:30 - ALERT - Type: FAILED_LOGIN | IP: 192.168.1.105 | Details: Failed login attempt for username: admin
```

**Breakdown:**
- **ALERT tag:** Marks as security event
- **Type:** Category of alert
- **IP:** Attacker's IP
- **Details:** What was attempted

### Common Alert Types

| Alert Type | Meaning | Severity |
|------------|---------|----------|
| FAILED_LOGIN | Wrong credentials | Medium |
| INVALID_LOGIN | Malicious username pattern | High |
| INVALID_ORDER | Malicious order data | High |
| UNAUTHORIZED_ACCESS | Access without login | Medium |
| PRIVILEGE_ESCALATION | User trying to access admin | High |
| 404_ERROR | Attempted unknown path | Low |
| 500_ERROR | Server error occurred | Medium |

---

## Blue Team Best Practices Demonstrated

### 1. Know Your Normal
- Establish baseline of normal activity
- Access logs show typical user behavior
- Deviations indicate potential threats

### 2. Defense Through Visibility
- Can't defend what you can't see
- Comprehensive logging enables detection
- Real-time monitoring enables response

### 3. Layered Security
- No single point of failure
- Multiple detection mechanisms
- Defense in depth approach

### 4. Assume Breach
- Monitor for lateral movement (privilege escalation)
- Track all admin actions
- Maintain audit trail

### 5. Continuous Improvement
- Review logs regularly
- Update detection patterns
- Adapt to new threats

---

## Future Security Enhancements

### Planned Features

1. **Rate Limiting**
   - Limit login attempts per IP
   - Temporary IP blocking
   - CAPTCHA after multiple failures

2. **Intrusion Detection**
   - Automated threat scoring
   - Behavioral analysis
   - Anomaly detection

3. **Enhanced Monitoring**
   - Real-time dashboard
   - Alert notifications
   - Automated response actions

4. **Compliance Features**
   - PCI DSS compliance (if handling payments)
   - GDPR data protection
   - SOC 2 audit trails

---

## Conclusion

This security implementation demonstrates blue team principles through:

  **Detection:** Multiple mechanisms to identify threats  
  **Logging:** Comprehensive audit trail  
  **Response:** Real-time alerts and monitoring  
  **Education:** Clear documentation and testing  
  **Real-world applicability:** Practical security measures

The system prioritizes **visibility and monitoring** over simple prevention, which is the hallmark of effective blue team operations.

---

**Document Version:** 1.0  
**Last Updated:** February 2025  
**Classification:** Educational - Blue Team Training
