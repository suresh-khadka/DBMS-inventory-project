# Troubleshooting Guide

## Common Issues and Solutions

---

## Installation Issues

### Issue: Python not found
**Error:** `python: command not found`

**Solution:**
- Install Python 3.8+
- Add Python to PATH
- Use `python3` instead of `python`

### Issue: pip not found
**Solution:**
```bash
python -m ensurepip --upgrade
python -m pip install --upgrade pip
```

### Issue: Virtual environment activation fails
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

---

## Database Issues

### Issue: Access denied for MySQL user
**Error:** `Access denied for user 'root'@'localhost'`

**Solution:**
1. Check .env file DB_PASSWORD
2. Test MySQL login: `mysql -u root -p`
3. Reset MySQL password if needed

### Issue: Database doesn't exist
**Solution:**
```sql
mysql -u root -p
CREATE DATABASE inventory_db;
EXIT;
```

### Issue: Migration fails
**Solution:**
```bash
# Delete migrations
rm inventory/migrations/0*.py

# Recreate
python manage.py makemigrations inventory
python manage.py migrate
```

---

## Django Issues

### Issue: ModuleNotFoundError
**Error:** `No module named 'rest_framework'`

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: PyMySQL version error
**Error:** `mysqlclient 2.2.1 or newer is required`

**Solution:**
- Already fixed in `inventory_system/__init__.py`
- Verify file contains version override

### Issue: Static files not loading
**Solution:**
```bash
python manage.py collectstatic --noinput
```

---

## Barcode Issues

### Issue: Barcode not generating
**Solution:**
- Check models.py has generate_barcode method
- Verify product name is provided
- Check database constraints

### Issue: Duplicate barcode
**Solution:**
- System auto-handles duplicates
- Check uniqueness constraint
- View inventory logs

---

## Frontend Issues

### Issue: 404 on login page
**Solution:**
- Check frontend files in frontend/
- Verify STATICFILES_DIRS in settings.py
- Run collectstatic

### Issue: API calls failing
**Solution:**
- Check backend is running
- Verify API_URL in js/api.js
- Check browser console for errors

### Issue: CORS errors
**Solution:**
- Check CORS settings in settings.py
- Verify CORS_ALLOW_ALL_ORIGINS=True

---

## Performance Issues

### Issue: Slow queries
**Solution:**
- Add database indexes
- Optimize queries
- Use select_related/prefetch_related

### Issue: High memory usage
**Solution:**
- Limit query results
- Implement pagination
- Clear old logs

---

## API Issues

### Issue: Authentication fails
**Solution:**
- Check username/password
- Verify token in request
- Check token expiration

### Issue: Permission denied
**Solution:**
- Check user role
- Verify permissions
- Check view decorators

---

## Production Issues

### Issue: DEBUG=False errors
**Solution:**
- Set ALLOWED_HOSTS
- Configure static files properly
- Set up proper logging

### Issue: Static files not serving
**Solution:**
```python
# settings.py
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```
```bash
python manage.py collectstatic
```

---

## Quick Diagnostics

### Check Python version:
```bash
python --version
```

### Check Django installation:
```bash
python -c "import django; print(django.get_version())"
```

### Check database connection:
```bash
python manage.py dbshell
```

### Check migrations:
```bash
python manage.py showmigrations
```

### Check for errors:
```bash
python manage.py check
```

---

## Getting Help

1. Check documentation
2. Review error messages
3. Check logs in logs/
4. Test with sample data
5. Contact support

---

**Most issues can be solved by:**
- Reading error messages carefully
- Checking configuration files
- Verifying environment setup
- Testing with fresh database
