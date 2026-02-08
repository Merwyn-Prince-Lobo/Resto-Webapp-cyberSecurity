# Lab Mode Setup - SQL Injection Training Environment

## Overview

This document explains how to enable and safely use the controlled SQL injection vulnerability in the Restaurant Management System for cybersecurity training purposes.

## ⚠️ CRITICAL SECURITY WARNING

**This vulnerability is INTENTIONAL and ONLY for authorized training environments.**

- ❌ **NEVER enable LAB_MODE in production or on public networks**
- ❌ **NEVER deploy this application with LAB_MODE enabled to production servers**
- ✅ **ONLY use this in isolated lab/training environments with authorized personnel**
- ✅ **Disable LAB_MODE (set to `False`) for all production deployments**

---

## How to Enable Lab Mode

### Step 1: Enable LAB_MODE Flag

Edit `app.py` and change:

```python
# Lab Mode Configuration - Set to True only for authorized training/labs
LAB_MODE = False  # Change to True to enable vulnerability
```

To:

```python
LAB_MODE = True  # Vulnerability enabled for training
```

### Step 2: Restart the Application

```bash
python app.py
```

### Step 3: Access Lab Endpoint

Once the application is running, access the vulnerable endpoint at:

```
http://localhost:5000/lab/billing
```

---

## Lab Vulnerability Details

### Vulnerable Endpoint: `/lab/billing`

**Location:** `app.py` - `lab_billing()` function

**Vulnerability Type:** SQL Injection (String Concatenation)

**What's Vulnerable:**
```python
query = f"SELECT * FROM secret_coupons WHERE coupon_code = '{coupon_code}'"
cursor.execute(query)
```

**Why It's Vulnerable:**
- User input (`coupon_code`) is directly concatenated into SQL query
- No parameterized queries or input validation
- Attacker can break out of the string and execute arbitrary SQL

### Hidden Trap Table: `secret_coupons`

This table is intentionally hidden and not referenced in the UI:

```sql
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

**Trap Coupon:**
- Code: `TRAP_SQLI_EXPLOIT`
- Discount: 99%
- Is_trap: 1 (indicates this is a security trap)

---

## Attack Scenarios for Training

### Scenario 1: Basic SQL Injection

**Input:** `' OR '1'='1`

**Injected Query:**
```sql
SELECT * FROM secret_coupons WHERE coupon_code = '' OR '1'='1'
```

**Result:** Returns all coupons from the table

---

### Scenario 2: Enumerate All Tables

**Input:** `' UNION SELECT name,2,3,4,5,6,7 FROM sqlite_master WHERE type='table' --`

**Purpose:** List all tables in the database including the hidden `secret_coupons` table

---

### Scenario 3: Retrieve Trap Coupon

**Input:** `' UNION SELECT coupon_code, discount_percentage, is_trap, 0, 0, 0 FROM secret_coupons --`

**Result:** Attacker discovers and retrieves the trap coupon

---

### Scenario 4: Claim Trap Coupon

**Input:** `TRAP_SQLI_EXPLOIT`

**Result:** 
- System logs the user as an "SQLI_EXPLOITER"
- Alert appears: "🚨 ALERT - SQLI_EXPLOITER detected"
- Entry created in security logs
- User flagged in exploiters database

---

## Exploit Detection Mechanism

### How It Works

1. **User submits coupon code** via `/lab/billing` endpoint
2. **Unsafe query executes** with the user input
3. **System checks if result is a trap coupon** using `check_trap_coupon()` function
4. **If trap detected:**
   - Alert logged as type `SQLI_EXPLOITER`
   - Timestamp recorded
   - User information stored
   - Message displayed to attacker

### Log Entries

**Security Alert Log Example:**
```
2025-02-07 10:15:32 - ALERT - Type: SQLI_EXPLOITER | IP: 192.168.1.100 | Details: User attacker claimed trap coupon: TRAP_SQLI_EXPLOIT - Likely SQL injection exploitation
```

---

## Monitoring and Viewing Results

### As Administrator

1. **Login** using admin credentials
2. **Navigate** to Admin Dashboard
3. **View options:**
   - **Security Logs** (`/admin/logs`) - General security alerts
   - **Exploiters Detection** (`/admin/exploiters`) - Users who claimed trap coupons

### Example Admin View

The Exploiters Detection page shows:

```
SQLInjection Exploiters Detection
==================================
Trap Coupon Code      | Claimed By  | Date/Time
TRAP_SQLI_EXPLOIT     | attacker    | 2025-02-07 10:15:32
```

---

## Important Security Notes

### What's Protected in Production Mode

All other routes use **parameterized queries**:

```python
# ✅ SAFE - Used everywhere except /lab/billing
cursor.execute("SELECT * FROM coupons WHERE code = ?", (user_input,))
```

### Routes Using Safe Queries

- `/register` - User account creation
- `/login` - Authentication
- `/order` - Order placement
- `/menu` - Menu retrieval
- `/admin/orders` - Order administration
- Any production route

### Routes With Intentional Vulnerability

- `/lab/billing` - **ONLY when LAB_MODE = True**

---

## Lab Exercises

### Exercise 1: SQL Injection Basics

**Objective:** Retrieve all coupons using UNION SELECT

**Steps:**
1. Access `/lab/billing`
2. Try the UNION SELECT payload
3. Review results in security logs

### Exercise 2: Table Enumeration

**Objective:** Discover the hidden `secret_coupons` table

**Steps:**
1. Use `sqlite_master` enumeration
2. List all database tables
3. Note: Other tables also visible (users, orders, sqlite_seq)

### Exercise 3: Trap Detection

**Objective:** Successfully retrieve and claim the trap coupon

**Steps:**
1. Find the hidden `secret_coupons` table using SQL injection
2. Retrieve `TRAP_SQLI_EXPLOIT` coupon code
3. Submit it to claim the coupon
4. Login as admin and check `/admin/exploiters`
5. Verify your username appears as an exploiter

### Exercise 4: Error-Based Injection

**Objective:** Extract data using error messages

**Steps:**
1. Try simple injections to generate errors
2. Review the error logging
3. Note how errors appear in security alerts

---

## Conclusion

This lab environment provides a safe space to:
- Understand SQL injection vulnerabilities
- Practice exploitation techniques
- Learn detection mechanisms
- See how logging can flag attackers
- Compare safe vs. unsafe coding patterns

**Remember:** Always disable LAB_MODE in production!
