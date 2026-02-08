# Lab Mode Testing Guide

## Pre-Testing Checklist

- [ ] Application is running: `python app.py`
- [ ] Database has been initialized
- [ ] You have registered a test user account
- [ ] You are logged in as the test user
- [ ] Admin account exists (username: admin, password: admin123)

---

## Test 1: Lab Mode Disabled (Default)

### Steps:
1. Verify `LAB_MODE = False` in `app.py`
2. Restart the application
3. While logged in, navigate to: `http://localhost:5000/lab/billing`

### Expected Result:
- ✅ Should redirect to menu or show 403 Forbidden
- ✅ Security log should show: `LAB_MODE_DISABLED` alert

### Commands to Check Logs:
```bash
tail logs/security_alerts.log
```

---

## Test 2: Enable Lab Mode

### Steps:
1. Edit `app.py`
2. Change line 23: `LAB_MODE = True`
3. Save the file
4. Restart the application
5. Navigate to: `http://localhost:5000/lab/billing`

### Expected Result:
- ✅ Should load the lab billing page
- ✅ Form to enter coupon code should be visible
- ✅ Educational information displayed

---

## Test 3: Normal Coupon Entry (No SQL Injection)

### Steps:
1. Ensure Lab Mode is enabled
2. Access `/lab/billing`
3. Enter any random text: `test123`
4. Click "Apply Coupon"

### Expected Result:
- ✅ Flash message: "Coupon not found."
- ✅ Access log shows: `LAB_BILLING_ATTEMPT`
- ✅ No trap detected alert

---

## Test 4: Basic SQL Injection

### Steps:
1. Access `/lab/billing` (LAB_MODE enabled)
2. Enter payload: `' OR '1'='1' --`
3. Submit form

### Expected Result:
- ✅ Should return results (SQL injection worked)
- ✅ Likely returns multiple coupons
- ✅ No trap alert (unless trap coupon is in results)
- ✅ Log shows: `LAB_BILLING_ATTEMPT` with the payload

---

## Test 5: Enumerate Database Tables

### Steps:
1. Access `/lab/billing` (LAB_MODE enabled)
2. Enter payload: `' UNION SELECT name,2,3,4,5,6,7 FROM sqlite_master WHERE type='table' --`
3. Submit form

### Expected Result:
- ✅ Returns database table names
- ✅ Should see `secret_coupons` table name
- ✅ Proves you can enumerate tables
- ✅ Log shows the injection attempt

---

## Test 6: Retrieve Trap Coupon (Exploitation Success)

### Steps:
1. Access `/lab/billing` (LAB_MODE enabled)
2. Enter payload: `' UNION SELECT coupon_code, discount_percentage, is_trap, 0, 0, 0 FROM secret_coupons --`
3. Submit form

### Expected Result:
- ✅ Returns coupon code: `TRAP_SQLI_EXPLOIT`
- ✅ Discount shown: 99%

---

## Test 7: Claim Trap Coupon (Trigger Exploit Alert)

### Steps:
1. Access `/lab/billing` (LAB_MODE enabled)
2. Enter the trap coupon code: `TRAP_SQLI_EXPLOIT`
3. Submit form

### Expected Result:
- ✅ Flash message: "🚨 SECURITY ALERT: Trap coupon detected! This incident has been logged."
- ✅ Alert logged as `SQLI_EXPLOITER` in security_alerts.log
- ✅ Database updated: claimed_by and claimed_at filled

### Verify in Logs:
```bash
grep "SQLI_EXPLOITER" logs/security_alerts.log
```

Should show:
```
2025-02-07 XX:XX:XX - ALERT - Type: SQLI_EXPLOITER | IP: 127.0.0.1 | Details: User [username] claimed trap coupon: TRAP_SQLI_EXPLOIT - Likely SQL injection exploitation
```

---

## Test 8: Admin Exploiters Dashboard

### Steps:
1. Login as admin (username: admin, password: admin123)
2. Go to Admin Dashboard
3. Navigate to: `http://localhost:5000/admin/exploiters`
4. OR click the "Exploiters Detection" link (if added to dashboard)

### Expected Result:
- ✅ Page loads showing exploiters table
- ✅ Your username appears in the list
- ✅ Trap coupon code: `TRAP_SQLI_EXPLOIT`
- ✅ Timestamp of when trap was claimed
- ✅ Red "🚨 EXPLOITER" badge shown

---

## Test 9: Verify Production Routes Are Safe

### Steps:
1. Try SQL injection in `/login` endpoint:
   - Username: `' OR '1'='1`
   - Password: `anything`
2. Try SQL injection in `/register` endpoint
3. Try SQL injection in order placement

### Expected Result:
- ✅ All attempts fail because parameterized queries are used
- ✅ Alert logged: `INVALID_LOGIN` or `INVALID_REGISTRATION` etc.
- ✅ No actual SQL injection occurs
- ✅ Input validation blocks the attempts

---

## Test 10: Disable Lab Mode Again

### Steps:
1. Edit `app.py`
2. Change `LAB_MODE = True` back to `LAB_MODE = False`
3. Restart application
4. Try to access `/lab/billing`

### Expected Result:
- ✅ Should get 403 Forbidden or redirect
- ✅ Alert logged: `LAB_MODE_DISABLED`
- ✅ Vulnerability is no longer accessible

---

## Testing Summary

| Test | Expected Result | Status |
|------|-----------------|--------|
| Lab Mode OFF | Access denied | ⬜ |
| Lab Mode ON | Page loads | ⬜ |
| Normal entry | Not found | ⬜ |
| SQL Injection basics | Results returned | ⬜ |
| Table enumeration | Tables listed | ⬜ |
| Trap retrieval | Secret coupon found | ⬜ |
| Trap claim | SQLI_EXPLOITER alert | ⬜ |
| Admin dashboard | Exploiter listed | ⬜ |
| Production safe | All injection blocked | ⬜ |
| Disable lab mode | Access denied again | ⬜ |

---

## Troubleshooting

### Lab endpoint not loading (LAB_MODE enabled)
- Verify `LAB_MODE = True` is set
- Check application is restarted
- Check database initialized: `restaurant.db` exists

### Trap coupon not found
- Verify `secret_coupons` table exists
- Run: `SELECT * FROM secret_coupons;` in SQLite
- Check trap coupon was inserted

### Exploit alert not logging
- Verify `logs/` directory exists
- Check file permissions on `security_alerts.log`
- Verify `check_trap_coupon()` is called

### Admin exploiters page is empty
- Verify you're logged in as admin
- Verify you've actually claimed the trap coupon
- Check database: `SELECT * FROM secret_coupons WHERE is_trap=1;`

---

## Demonstration Scenario

A typical demonstration flow for training:

1. **Show Normal Operation** (LAB_MODE OFF)
   - Login, view menu, place order
   - Everything works normally
   
2. **Enable Lab Mode**
   - Change LAB_MODE = True
   - Restart

3. **Demonstrate SQL Injection**
   - Show basic injection returning results
   - Show table enumeration
   - Find hidden table

4. **Show Exploitation Detection**
   - Try to claim trap coupon
   - Show alert logged
   - View admin exploiters dashboard

5. **Teach Secure Coding**
   - Compare vulnerable code vs. safe code
   - Show input validation
   - Demonstrate parameterized queries

6. **Disable Lab Mode**
   - Show LAB_MODE = False
   - Vulnerability is now inaccessible

---

## Clean Up After Training

1. **Disable Lab Mode**
   ```python
   LAB_MODE = False
   ```

2. **Optional: Reset database**
   ```bash
   rm restaurant.db
   ```
   (This will create a fresh database on next run)

3. **Optional: Clear logs**
   ```bash
   rm logs/security_alerts.log
   rm logs/access.log
   ```

4. **Restart application**
   ```bash
   python app.py
   ```

---

## Success Criteria

You have successfully completed the lab if you can:

✅ Enable/disable lab mode with the configuration flag
✅ Access the vulnerable billing endpoint only when lab mode is on
✅ Execute SQL injection payload on the vulnerable endpoint
✅ Find the hidden `secret_coupons` table using enumeration
✅ Retrieve the trap coupon code: `TRAP_SQLI_EXPLOIT`
✅ Claim the trap coupon and trigger exploit detection
✅ View yourself in the exploiters list as admin
✅ Verify all production routes remain secure
✅ Understand the difference between unsafe and safe queries
✅ Appreciate the value of security logging and monitoring
