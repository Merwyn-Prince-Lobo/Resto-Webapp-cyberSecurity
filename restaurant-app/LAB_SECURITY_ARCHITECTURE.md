# Lab Mode Security Architecture

## System Overview

This document explains the security architecture of the lab mode implementation, focusing on how the trap detection mechanism works and maintains security throughout the application.

```
┌─────────────────────────────────────────────────────────┐
│     Restaurant Management Web Application               │
│     (Secure - All routes use parameterized queries)     │
└─────────────────────────────────────────────────────────┘
                           │
                ┌──────────┼──────────┐
                │                    │
        ┌──────▼─────────┐    ┌────▼──────────┐
        │ Production      │    │ Lab Mode       │
        │ Routes (Secure) │    │ Routes (Trap)  │
        └─────────────────┘    └───────────────┘
                │                    │
        Uses Parameterized     Uses String
        Queries Everywhere      Concatenation
        (✅ Safe)              (⚠️ Vulnerable)
                │                    │
                │              LAB_MODE = ?
                │              /          \
                │          False          True
                │            │             │
         Always Safe    Blocked (403)   Enabled
```

---

## Design Principles

### 1. Separation of Concerns
- **Lab code** is isolated in `/lab/billing` endpoint
- **Production code** uses safe patterns everywhere else
- **No cross-contamination** of security mechanisms
- **Clear boundaries** between vulnerable and safe code

### 2. Defense in Depth
- **Configuration Flag**: Lab mode must be explicitly enabled
- **Database Design**: Trap table completely separate
- **Exploit Detection**: Additional layer catches exploitation attempts
- **Logging System**: Complete audit trail of all activities

### 3. Principle of Least Privilege
- **Lab endpoint** is NOT accessible in production mode
- **Trap coupon** is not used in normal operations
- **Exploit alerts** are clearly labeled and logged
- **Admin access** required to view exploiter dashboard

---

## Threat Model

### What We're Protecting Against

1. **Accidental activation** - Lab vulnerability enabled in production
2. **Unauthorized exploitation** - Users trying to exploit the system
3. **Detection evasion** - Attackers trying to hide their actions
4. **Damage escalation** - Limiting scope of lab to isolated endpoint

### What We Allow

1. ✅ Authorized security training personnel using the lab
2. ✅ SQL injection attempts on the vulnerable endpoint only
3. ✅ Database enumeration in controlled environment
4. ✅ Full exploitation of the intentional vulnerability

### What We Prevent

1. ❌ Lab activation in production (removed by default)
2. ❌ Exploitation of production routes (all safe)
3. ❌ Authentication bypass (separate security layers)
4. ❌ Data exfiltration (limited to lab-only tables)

---

## Trap Detection Mechanism

### Architecture Flow

```
User Claims Coupon
        │
        ▼
Coupon retrieved from database
        │
        ├─ Normal coupon (is_trap = 0)
        │  └─> Display discount, continue normally
        │
        └─ Trap coupon (is_trap = 1)
           └─> check_trap_coupon() function
               │
               ├─> Log alert: SQLI_EXPLOITER
               ├─> Record username & timestamp
               ├─> Update database: claimed_by, claimed_at
               └─> Display warning to user
```

### Key Functions

#### 1. `check_trap_coupon(coupon_code, username)` - Lines 163-184
```python
def check_trap_coupon(coupon_code, username):
    """Check if a coupon is a trap for SQL injection exploiters"""
    
    # Query using safe parameterized query
    cursor.execute(
        "SELECT is_trap, claimed_by FROM secret_coupons WHERE coupon_code = ?",
        (coupon_code,)
    )
    result = cursor.fetchone()
    
    # Check if this is a trap
    if result and result['is_trap'] == 1:
        # LOG THE ALERT
        log_alert('SQLI_EXPLOITER', 
                 f'User {username} claimed trap coupon: {coupon_code}')
        
        # UPDATE DATABASE - RECORD THE EXPLOITATION
        cursor.execute(
            "UPDATE secret_coupons SET claimed_by = ?, claimed_at = ? WHERE coupon_code = ?",
            (username, datetime.now(), coupon_code)
        )
        conn.commit()
        
        return True  # Indicate this is a trap
    return False
```

#### 2. `log_alert(alert_type, details)` - Lines 158-161
```python
def log_alert(alert_type, details):
    """Log security alerts"""
    ip = request.remote_addr
    msg = f"Type: {alert_type} | IP: {ip} | Details: {details}"
    alert_logger.warning(msg)  # Written to security_alerts.log
```

#### 3. Vulnerable Query in `/lab/billing` - Lines 485-492
```python
if LAB_MODE:
    # VULNERABLE: Using string concatenation
    query = f"SELECT * FROM secret_coupons WHERE coupon_code = '{coupon_code}'"
    cursor.execute(query)
else:
    # SAFE: Using parameterized query
    cursor.execute("SELECT * FROM secret_coupons WHERE coupon_code = ?", (coupon_code,))
```

---

## Data Flow Diagram

### Successful Exploitation Scenario

```
┌─────────────────────────────────────────────────────────────┐
│ Attacker discovers hidden table via table enumeration       │
│ SQL: ' UNION SELECT name FROM sqlite_master --              │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│ Attacker retrieves all coupon codes from secret_coupons     │
│ SQL: ' UNION SELECT coupon_code FROM secret_coupons --      │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│ Attacker discovers trap coupon: TRAP_SQLI_EXPLOIT           │
│ (This is the objective of the lab exercise)                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│ Attacker submits TRAP_SQLI_EXPLOIT as coupon_code          │
│ POST: /lab/billing with coupon_code=TRAP_SQLI_EXPLOIT       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│ System retrieves coupon (parameterized query processing)    │
│ Result found with is_trap = 1                               │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│ check_trap_coupon() detects trap                            │
│ Alert logged: SQLI_EXPLOITER                                │
│ Database updated: claimed_by=username, claimed_at=now       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│ User sees warning: "SECURITY ALERT: Trap coupon detected"   │
│ Admin sees user in /admin/exploiters listing                │
└─────────────────────────────────────────────────────────────┘
```

---

## Security Guarantees

### Guarantee 1: Lab Mode Containment
**Promise**: Vulnerability only affects `/lab/billing` endpoint

**Mechanism**:
- All other endpoints use parameterized queries (lines 258-409)
- Lab endpoint only active when `LAB_MODE = True` AND user accesses `/lab/billing`
- Separate database table isolated from operational tables

**Verification**: Run grep:
```bash
grep -n "cursor.execute" app.py
# All except lab endpoint use parameterized queries with '?'
```

### Guarantee 2: Exploit Detection
**Promise**: System automatically detects and logs exploitation attempts

**Mechanism**:
- Trap coupon designed to be discovered via exploitation
- `check_trap_coupon()` triggers alert on trap claim
- Real-time logging to `security_alerts.log`
- Admin dashboard shows all exploiters

**Verification**:
```bash
grep "SQLI_EXPLOITER" logs/security_alerts.log
# Should contain all exploitation attempts
```

### Guarantee 3: Production Safety
**Promise**: Normal users are completely unaffected

**Mechanism**:
- Lab endpoint requires login (production routes do too)
- Trap table not referenced anywhere normal users go
- Normal operations use `/order`, `/menu`, `/my-orders` etc. (all safe)
- Lab-only table `secret_coupons` not integrated into normal flow

**Verification**:
- User registration: Uses safe queries ✅
- User login: Uses safe queries ✅
- Order placement: Uses safe queries ✅
- Order viewing: Uses safe queries ✅

### Guarantee 4: Audit Trail
**Promise**: Complete record of all security events

**Mechanism**:
- Every access logged to `access.log`
- Every alert logged to `security_alerts.log`
- Lab endpoint logs all attempts
- Exploit attempts logged with IP address

**Sample Audit Trail**:
```
[Access Log]
2025-02-07 10:00:00 - IP: 192.168.1.100 | Action: LOGIN | User: trainee1

[Security Log]
2025-02-07 10:01:00 - ALERT - Type: LAB_BILLING_ATTEMPT | IP: 192.168.1.100 | Details: ...

[Security Log]
2025-02-07 10:05:00 - ALERT - Type: SQLI_EXPLOITER | IP: 192.168.1.100 | trainee1 claimed TRAP_SQLI_EXPLOIT
```

---

## Defense Layers

```
Layer 1: Configuration
├─ LAB_MODE = False (default)
└─ Can only be changed by developer/admin

Layer 2: Access Control
├─ Endpoint requires login (@login_required)
├─ Only exists at /lab/billing URL
└─ Returns 403 if LAB_MODE is False

Layer 3: Operational Isolation
├─ Separate database table (secret_coupons)
├─ Not used by any production route
└─ Only accessed via vulnerable endpoint

Layer 4: Trap Detection
├─ Identifies exploitation attempts
├─ Records exploiter information
└─ Triggers security alert type

Layer 5: Logging & Monitoring
├─ All attempts logged with timestamp & IP
├─ Admin dashboard shows exploiters
└─ Real-time security alert file
```

---

## Code Review Checklist

Use this to verify the security implementation:

- [ ] `LAB_MODE` is defined as `False` by default (line 23)
- [ ] All production routes use `?` placeholders, not f-strings
- [ ] `/lab/billing` checks `if not LAB_MODE:` and returns 403 (lines 464-466)
- [ ] Vulnerable query uses f-string ONLY when `LAB_MODE==True` (line 488)
- [ ] `secret_coupons` table created in `init_db()` (lines 88-96)
- [ ] Trap coupon inserted with `is_trap=1` (lines 98-103)
- [ ] `check_trap_coupon()` uses parameterized query to detect trap (line 168)
- [ ] Alert logged with type `SQLI_EXPLOITER` (lines 174-176)
- [ ] Admin dashboard protected with `@admin_required` (line 412)

---

## Conclusion

The lab mode implementation provides:

✅ **Safe by Default** - Vulnerability disabled by default
✅ **Isolated** - Only affects one endpoint
✅ **Detectable** - Traps catch exploitation attempts
✅ **Observable** - Comprehensive logging and monitoring
✅ **Educationally Valuable** - Teaches both attack and defense
✅ **Production Safe** - Zero risk to normal operations

The system demonstrates that security testing environments can be valuable educational tools when properly isolated, controlled, and monitored.
