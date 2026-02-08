# Lab Mode Implementation Summary

## Overview
A controlled SQL injection vulnerability training module has been successfully added to the Restaurant Management Web Application. This is designed exclusively for cybersecurity training in isolated lab environments.

## What Was Implemented

### 1. **Laboratory Mode Toggle** 
- **File:** `app.py` (line 23)
- **Configuration:** `LAB_MODE = False` (default - safe)
- **Purpose:** Enables/disables the intentional vulnerability
- **Status:** ✅ Only activates when explicitly set to `True`

### 2. **Hidden Database Table**
- **Table Name:** `secret_coupons` (not referenced in UI)
- **Created in:** `init_db()` function
- **Contains:**
  - `coupon_code` - Unique coupon identifier
  - `discount_percentage` - Discount value
  - `is_trap` - Flag indicating trap coupon (1 = trap)
  - `claimed_by` - User who claimed it
  - `claimed_at` - Timestamp of claim

- **Trap Coupon Inserted:** 
  - Code: `TRAP_SQLI_EXPLOIT`
  - Discount: 99%
  - Is_trap: 1

### 3. **Vulnerable Endpoint: `/lab/billing`**
- **File:** `app.py` (lines 448-526)
- **Route Decorator:** `@app.route('/lab/billing', methods=['GET', 'POST'])`
- **Vulnerability Type:** SQL Injection via string concatenation
- **Vulnerable Code:**
  ```python
  query = f"SELECT * FROM secret_coupons WHERE coupon_code = '{coupon_code}'"
  cursor.execute(query)
  ```
- **Activation:** Only processes when `LAB_MODE = True`
- **Protection:** Returns 403 Forbidden if `LAB_MODE = False`

### 4. **Exploit Detection Function**
- **Function Name:** `check_trap_coupon()` (lines 163-184)
- **Location:** `app.py`
- **Detects:** When a user successfully retrieves and claims the trap coupon
- **Action on Detection:**
  - Logs alert type: `SQLI_EXPLOITER`
  - Records timestamp
  - Updates database with claimed_by username
  - Displays warning to user

### 5. **Lab Billing Template**
- **File:** `templates/lab_billing.html`
- **Features:**
  - Lab environment notice banner
  - Coupon submission form
  - Results display with trap detection notification
  - Educational information about SQL injection
  - Safe vs. unsafe query patterns shown
  - Instructions for discovering hidden table

### 6. **Exploiters Detection Dashboard**
- **File:** `templates/admin_exploiters.html`
- **Endpoint:** `/admin/exploiters`
- **Access:** Admin-only (`@admin_required` decorator)
- **Displays:**
  - List of all trap coupons claimed by users
  - Usernames of exploiters
  - Timestamps of exploitation
  - Visual alerts for security context

### 7. **Admin Endpoint: `/admin/exploiters`**
- **File:** `app.py` (lines 412-422)
- **Purpose:** Display users who exploited SQL injection
- **Query:** Uses safe parameterized query to retrieve trap coupon claims
- **Access Control:** Admin-only via `@admin_required` decorator

### 8. **Documentation Files**

#### `LAB_MODE_SETUP.md` (Comprehensive Guide)
- Detailed setup instructions
- Security warnings
- Vulnerability explanation
- Attack scenarios with examples
- Exercise walkthroughs
- Exploit detection explanation
- Monitoring and viewing instructions

#### `LAB_MODE_README.md` (Quick Reference)
- Quick enable instructions
- Test payloads
- Admin access URL
- Production safety reminder

## Security Architecture

### Production Routes (All Safe - Parameterized Queries)
✅ `/register` - User registration
✅ `/login` - Authentication  
✅ `/order` - Order placement
✅ `/menu` - Menu retrieval
✅ `/my-orders` - User order viewing
✅ `/admin/orders` - Admin order management
✅ `/admin/update-order/<id>` - Order status updates
✅ `/logout` - User logout

### Lab-Only Route (Protected)
⚠️ `/lab/billing` - Vulnerable endpoint (only when LAB_MODE enabled)

## Traffic Pattern

```
User Submits Coupon
         ↓
LAB_MODE Check → If False: Return 403 Forbidden
         ↓ (If True)
Unsafe Query Execution
         ↓
Result Processing
         ↓
Trap Detection → If trap coupon claimed:
                  - Log SQLI_EXPLOITER alert
                  - Record in database
                  - Display warning
         ↓
Response to User
```

## Logging System

### Alert Categories
- `SQLI_EXPLOITER` - User claimed trap coupon (indicates SQL injection exploitation)
- `LAB_MODE_DISABLED` - Unauthorized lab access attempt
- `LAB_BILLING_ERROR` - Database errors during vulnerable query

### Log Locations
- **Security Alerts:** `logs/security_alerts.log`
- **Access Logs:** `logs/access.log`

### Example Alert Entry
```
2025-02-07 14:32:15 - ALERT - Type: SQLI_EXPLOITER | IP: 192.168.1.100 | Details: User attacker123 claimed trap coupon: TRAP_SQLI_EXPLOIT - Likely SQL injection exploitation
```

## How to Use

### Enable Lab Mode
1. Edit `app.py`
2. Change `LAB_MODE = False` to `LAB_MODE = True`
3. Restart application

### Access Lab
- Visit: `http://localhost:5000/lab/billing`

### Test SQL Injection
```
' OR '1'='1' --
' UNION SELECT name,2,3,4,5,6,7 FROM sqlite_master WHERE type='table' --
TRAP_SQLI_EXPLOIT
```

### View Exploiters (As Admin)
- Visit: `http://localhost:5000/admin/exploiters`

## Safety Features

✅ **Isolated from Authentication** - Doesn't affect login/security
✅ **Isolated from Core Logic** - Separate endpoint only
✅ **Configurable Toggle** - Easy to disable
✅ **Access Control** - Requires login
✅ **Error Handling** - Logs errors without crashing
✅ **Trap Detection** - Automatically flags exploiters
✅ **Documentation** - Clear warnings and instructions
✅ **Parameterized Queries Elsewhere** - All other routes secure

## Testing Checklist

- [ ] LAB_MODE = False blocks access (returns 403)
- [ ] LAB_MODE = True allows access to `/lab/billing`
- [ ] Secret coupons table exists in database
- [ ] Trap coupon `TRAP_SQLI_EXPLOIT` exists
- [ ] Normal coupon entry works without SQL injection
- [ ] SQL injection payloads are executed
- [ ] Trap coupon claim is logged as `SQLI_EXPLOITER`
- [ ] Admin can view exploiters at `/admin/exploiters`
- [ ] All production routes still use parameterized queries
- [ ] Application runs without errors

## Important Reminders

⚠️ **CRITICAL SECURITY NOTES:**

1. **LAB_MODE MUST BE FALSE IN PRODUCTION**
   - Never deploy with LAB_MODE enabled
   - Never expose to public networks
   - Only use in isolated lab environments

2. **Authorized Personnel Only**
   - This is for authorized training
   - Not for malicious purposes
   - Follow your organization's security policies

3. **Production Routes Are Secure**
   - All normal application functions are protected
   - Only the lab-only endpoint has the vulnerability
   - No risk to normal users

4. **Documentation Is Key**
   - Trainees should read LAB_MODE_SETUP.md
   - Understand the concepts before attempting
   - Learn from the exploit detection mechanism
