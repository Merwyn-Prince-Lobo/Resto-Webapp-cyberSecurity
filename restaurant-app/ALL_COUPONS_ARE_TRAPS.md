# All Coupons Are Traps - Complete Guide

## Overview

**Changed:** All coupons in the system are now traps

**Impact:** Any coupon claimed = exploitation detected + user flagged

**Benefit:** Makes the system more interesting for red team testing

---

## The 10 Trap Coupons

| Coupon Code | Discount | Is Trap | Purpose |
|---|---|---|---|
| TRAP_SQLI_EXPLOIT | 99% | ✅ 1 | Original obvious trap |
| SUMMER2025 | 50% | ✅ 1 | Looks like seasonal promo |
| WELCOME50 | 50% | ✅ 1 | Looks like new user offer |
| DISCOUNT25 | 25% | ✅ 1 | Looks generic |
| PROMO_OFFER | 35% | ✅ 1 | Looks like marketing promo |
| FLAT_OFF_40 | 40% | ✅ 1 | Looks like flat discount |
| EXCLUSIVE_99 | 99% | ✅ 1 | Looks like exclusive deal |
| SAVE_NOW | 30% | ✅ 1 | Looks like time-limited |
| COUPON_HACK | 60% | ✅ 1 | Suspicious name |
| SECRET_CODE | 75% | ✅ 1 | Looks like insider secret |

---

## How Red Team Gets Caught

### Scenario 1: Direct Coupon Entry

Red Team enters any coupon code they discover:
```
http://localhost:5000/lab/billing
Coupon: SUMMER2025
↓
System checks: is_trap=1 ✓
↓
ALERT: SQLI_EXPLOITER logged
```

---

### Scenario 2: SQL Injection Discovery

Red Team uses SQL injection to find coupons:
```sql
' UNION SELECT coupon_code,discount_percentage,is_trap... FROM secret_coupons --
↓
Sees: 10 different coupon codes
↓
Thinks: "Great! Found the jackpot!"
↓
Tries any one: WELCOME50, SUMMER2025, etc.
↓
Boom! 🚨 Trapped!
```

---

### Scenario 3: Blind SQL Injection

Red Team extracts coupons blindly:
```
Extracts first coupon: TRAP_SQLI_EXPLOIT
Tries it: EXPLOIT_DETECTED ✓
↓
Extracts second coupon: SUMMER2025
Tries it: EXPLOIT_DETECTED ✓
↓
Extracts all 10... Every single one is a trap!
```

---

## Why This Is Brilliant

### Problem with Single Trap
- ❌ Red team finds 1 trap, tries it, gets caught
- ❌ They blame bad luck
- ❌ Could've been legitimate table

### Solution with All Traps
- ✅ Red team finds 10 coupons
- ✅ They think "surely not ALL are fake?"
- ✅ They try one... CAUGHT
- ✅ They try another... CAUGHT
- ✅ They try all 10... ALL CAUGHT
- ✅ They can't figure out which is legitimate
- ✅ Multiple alerts logged (one per coupon tried)
- ✅ Clear pattern of exploitation

---

## Attack Timeline

```
T+0:   Red Team discovers /lab/billing vulnerability
       ↓
T+5:   Use SQL injection to list all coupons
       SELECT * FROM secret_coupons
       ↓
       Result: 10 coupon codes found!
       ↓
T+10:  Try SUMMER2025 (looks legitimate)
       ↓
       🚨 ALERT: SQLI_EXPLOITER | claimed: SUMMER2025
       ↓
T+15:  "Hmm, bad luck. Try another one"
       Try WELCOME50
       ↓
       🚨 ALERT: SQLI_EXPLOITER | claimed: WELCOME50
       ↓
T+20:  "WTF? TWO traps??"
       Try DISCOUNT25
       ↓
       🚨 ALERT: SQLI_EXPLOITER | claimed: DISCOUNT25
       ↓
T+25:  "OH NO... Are they ALL traps??"
       [Realizes the exploit]
```

---

## Blue Team Benefits

### Detection

**Before (1 trap):**
- 1 alert per session
- Easy to dismiss as fluke

**After (10 traps):**
```
ALERT 1: User claimed TRAP_SQLI_EXPLOIT
ALERT 2: User claimed SUMMER2025
ALERT 3: User claimed WELCOME50
ALERT 4: User claimed DISCOUNT25
ALERT 5: User claimed PROMO_OFFER
ALERT 6: User claimed FLAT_OFF_40
ALERT 7: User claimed EXCLUSIVE_99
ALERT 8: User claimed SAVE_NOW
ALERT 9: User claimed COUPON_HACK
ALERT 10: User claimed SECRET_CODE

Pattern = Obvious SQL injection exploitation!
```

### Investigation

**Questions for red team:**
1. "Why did you try 3 different coupons?"
2. "How did you know these coupon codes existed?"
3. "No legitimate user tries 5 coupons in 10 minutes"
4. "Your SQL injection attempts are logged"

---

## Testing the New System

### Step 1: Reset Database
```bash
rm restaurant.db
python app.py
```

### Step 2: Create test account
```bash
# Register at /register or update DB
sqlite3 restaurant.db
UPDATE users SET role='admin' WHERE username='testuser';
```

### Step 3: View All Coupons

**Via SQL Injection:**
```
http://localhost:5000/lab/billing
Coupon: ' UNION SELECT coupon_code,discount_percentage,is_trap,4,5,6,7 FROM secret_coupons --
```

**Result: All 10 coupons visible**

### Step 4: Try Each Coupon

```
Try 1: TRAP_SQLI_EXPLOIT → 🚨 CAUGHT
Try 2: SUMMER2025 → 🚨 CAUGHT
Try 3: WELCOME50 → 🚨 CAUGHT
Try 4: DISCOUNT25 → 🚨 CAUGHT
...
Try 10: SECRET_CODE → 🚨 CAUGHT
```

---

## Logs Generated

### After Trying All 10 Coupons

```bash
grep "SQLI_EXPLOITER" logs/security_alerts.log
```

Output:
```
Type: SQLI_EXPLOITER | User: attacker | claimed: TRAP_SQLI_EXPLOIT
Type: SQLI_EXPLOITER | User: attacker | claimed: SUMMER2025
Type: SQLI_EXPLOITER | User: attacker | claimed: WELCOME50
Type: SQLI_EXPLOITER | User: attacker | claimed: DISCOUNT25
Type: SQLI_EXPLOITER | User: attacker | claimed: PROMO_OFFER
Type: SQLI_EXPLOITER | User: attacker | claimed: FLAT_OFF_40
Type: SQLI_EXPLOITER | User: attacker | claimed: EXCLUSIVE_99
Type: SQLI_EXPLOITER | User: attacker | claimed: SAVE_NOW
Type: SQLI_EXPLOITER | User: attacker | claimed: COUPON_HACK
Type: SQLI_EXPLOITER | User: attacker | claimed: SECRET_CODE
```

---

## Admin Dashboard

### View on `/admin/exploiters`

```
Trap Coupon Code  | Claimed By | Date/Time              | Status
TRAP_SQLI_EXPLOIT | attacker   | 2025-02-07 14:32:15    | 🚨 EXPLOITER
SUMMER2025        | attacker   | 2025-02-07 14:32:45    | 🚨 EXPLOITER
WELCOME50         | attacker   | 2025-02-07 14:33:12    | 🚨 EXPLOITER
DISCOUNT25        | attacker   | 2025-02-07 14:33:28    | 🚨 EXPLOITER
PROMO_OFFER       | attacker   | 2025-02-07 14:33:51    | 🚨 EXPLOITER
FLAT_OFF_40       | attacker   | 2025-02-07 14:34:10    | 🚨 EXPLOITER
EXCLUSIVE_99      | attacker   | 2025-02-07 14:34:33    | 🚨 EXPLOITER
SAVE_NOW          | attacker   | 2025-02-07 14:34:58    | 🚨 EXPLOITER
COUPON_HACK       | attacker   | 2025-02-07 14:35:15    | 🚨 EXPLOITER
SECRET_CODE       | attacker   | 2025-02-07 14:35:42    | 🚨 EXPLOITER

Total: 10 exploits detected from 1 attacker
```

---

## Database Query to Verify

```bash
sqlite3 restaurant.db
SELECT coupon_code, discount_percentage, is_trap, claimed_by FROM secret_coupons;
```

**Result:**
```
TRAP_SQLI_EXPLOIT    | 99    | 1   | [username or NULL]
SUMMER2025           | 50    | 1   | [username or NULL]
WELCOME50            | 50    | 1   | [username or NULL]
DISCOUNT25           | 25    | 1   | [username or NULL]
PROMO_OFFER          | 35    | 1   | [username or NULL]
FLAT_OFF_40          | 40    | 1   | [username or NULL]
EXCLUSIVE_99         | 99    | 1   | [username or NULL]
SAVE_NOW             | 30    | 1   | [username or NULL]
COUPON_HACK          | 60    | 1   | [username or NULL]
SECRET_CODE          | 75    | 1   | [username or NULL]
```

---

## Code Change Summary

### Before
```python
# Single trap coupon
cursor.execute(...)
if not cursor.fetchone():
    cursor.execute(
        "INSERT INTO secret_coupons ... VALUES (?, ?, ?, ?)",
        ('TRAP_SQLI_EXPLOIT', 99, 1, datetime.now())
    )
```

### After
```python
# 10 trap coupons - ALL are traps
trap_coupons = [
    ('TRAP_SQLI_EXPLOIT', 99, 1),
    ('SUMMER2025', 50, 1),
    ('WELCOME50', 50, 1),
    ('DISCOUNT25', 25, 1),
    ('PROMO_OFFER', 35, 1),
    ('FLAT_OFF_40', 40, 1),
    ('EXCLUSIVE_99', 99, 1),
    ('SAVE_NOW', 30, 1),
    ('COUPON_HACK', 60, 1),
    ('SECRET_CODE', 75, 1),
]

for coupon_code, discount, is_trap in trap_coupons:
    cursor.execute(...WHERE coupon_code = ?", (coupon_code,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO secret_coupons ... VALUES (?, ?, ?, ?)",
            (coupon_code, discount, is_trap, datetime.now())
        )
```

---

## Red Team Reaction

```
"Great! I found coupons!"
           ↓
"Let me try SUMMER2025..."
           ↓
"TRAP DETECTED?? 😡"
           ↓
"Must be a coincidence... Try WELCOME50"
           ↓
"TRAP DETECTED?? 😡😡"
           ↓
"Oh wait... Let me count... 10 coupons"
"I tried 10... all are traps..."
"THEY'RE ALL TRAPS?!?! 😱"
           ↓
"I got caught SO many times"
       ↓
"Lesson Learned: SQL Injection exploits get detected"
```

---

## What's Better About This

✅ **Clear Pattern Detection:** 10 alerts vs 1 alert (obvious suspicious activity)
✅ **More Realistic:** Real apps have multiple coupons
✅ **Training Value:** Shows layered defense + detection
✅ **Prevents Lucky Escapes:** Red team can't "accidentally" find legitimate coupons
✅ **Multiple Touchpoints:** Each coupon claim is an alert + database record
✅ **Admin Review:** Clear evidence of SQL injection exploitation

---

## Summary

**All 10 coupons have is_trap = 1**

Meaning:
- Any coupon claimed = Red team gets caught
- Any coupon used = Alert logged
- Any coupon in results = Exploitation detected
- Perfect trap with no escape route

**Setup:** Just reset database and restart app!

```bash
rm restaurant.db
python app.py
# Done! 10 traps ready.
```
