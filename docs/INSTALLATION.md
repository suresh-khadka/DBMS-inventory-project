# Installation Guide

## Complete Installation Instructions for Django Inventory Management System

---

## Prerequisites

### Required Software:
- Python 3.8 or higher
- MySQL 8.0 or higher (or XAMPP)
- pip (Python package manager)
- Git (optional)

### Optional:
- Docker & Docker Compose (for Docker installation)
- Postman (for API testing)

---

## Installation Methods

### Method 1: Automated Setup (Recommended)

#### Windows:
```bash
# Navigate to project folder
cd inventory-management-system

# Run setup script
scripts\setup.bat

# Server will start automatically
```

#### Linux/Mac:
```bash
# Navigate to project folder
cd inventory-management-system

# Make script executable
chmod +x scripts/setup.sh

# Run setup
./scripts/setup.sh
```

---

### Method 2: Manual Installation

#### Step 1: Clone or Extract Project
```bash
# If using Git
git clone <repository-url>

# Or extract ZIP file
```

#### Step 2: Create Virtual Environment
```bash
cd backend
python -m venv venv

# Activate virtual environment

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

**Dependencies installed:**
- Django 4.2.7
- djangorestframework 3.14.0
- django-cors-headers 4.3.1
- PyMySQL 1.1.0
- python-dotenv 1.0.0
- bcrypt 4.1.2
- PyJWT 2.8.0

#### Step 4: Configure Environment
```bash
# Copy environment template
copy .env.example .env

# Edit .env file
```

**Configure these settings:**
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=inventory_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
```

#### Step 5: Create MySQL Database
```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE inventory_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Verify
SHOW DATABASES;

# Exit
EXIT;
```

#### Step 6: Run Migrations
```bash
# Create migrations
python manage.py makemigrations inventory

# Apply migrations
python manage.py migrate
```

**Expected output:**
```
Applying contenttypes.0001_initial... OK
Applying auth.0001_initial... OK
Applying admin.0001_initial... OK
Applying inventory.0001_initial... OK
...
```

#### Step 7: Create Superuser
```bash
python manage.py createsuperuser

# Enter details:
Username: admin
Email: (optional)
Password: admin123
Password (again): admin123
```

#### Step 8: Create Sample Data (Optional)
```bash
python manage.py create_sample_data
```

**This creates:**
- 3 users (admin, worker, customer)
- 2 employees
- 1 customer
- 3 products with auto-generated barcodes

#### Step 9: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

#### Step 10: Start Development Server
```bash
python manage.py runserver
```

**Server starts at:** http://127.0.0.1:8000

---

### Method 3: Docker Installation

#### Requirements:
- Docker Desktop installed
- Docker Compose installed

#### Steps:
```bash
# Navigate to project
cd inventory-management-system

# Start containers
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

**Access:**
- Frontend: http://localhost:8000
- Backend API: http://localhost:8000/api
- Admin Panel: http://localhost:8000/admin

---

## Post-Installation Steps

### 1. Verify Installation
```bash
# Check Django version
python manage.py version

# Check database connection
python manage.py dbshell
```

### 2. Access Application
```
Frontend: http://localhost:8000
Admin Panel: http://localhost:8000/admin
API Root: http://localhost:8000/api
```

### 3. Test Login
**Default credentials:**
- Admin: admin / admin123
- Worker: worker1 / worker123
- Customer: customer1 / customer123

### 4. Test Barcode Generation
```bash
# Django shell
python manage.py shell
```

```python
from inventory.models import Product
from decimal import Decimal

product = Product.objects.create(
    product_name="Test Product",
    cost_price=Decimal("10.00"),
    selling_price=Decimal("15.00"),
    stock_level=50
)

print(f"Product: {product.product_name}")
print(f"Barcode: {product.barcode}")
# Output: Barcode: TESTPRODUC1234
```

---

## Troubleshooting

### Common Issues:

#### 1. MySQL Connection Error
**Error:** `Access denied for user 'root'@'localhost'`

**Solution:**
- Check DB_PASSWORD in .env
- Verify MySQL is running
- Test connection: `mysql -u root -p`

#### 2. Module Not Found
**Error:** `ModuleNotFoundError: No module named 'rest_framework'`

**Solution:**
```bash
pip install djangorestframework==3.14.0
```

#### 3. Migration Error
**Error:** `django.db.utils.OperationalError: (1824, "Failed to open the referenced table")`

**Solution:**
```bash
# Delete migrations
del inventory\migrations\0*.py

# Recreate database
DROP DATABASE inventory_db;
CREATE DATABASE inventory_db;

# Run migrations again
python manage.py makemigrations inventory
python manage.py migrate
```

#### 4. PyMySQL Error
**Error:** `mysqlclient 2.2.1 or newer is required`

**Solution:**
- Already fixed in `inventory_system/__init__.py`
- Verify file contains:
```python
import pymysql
pymysql.version_info = (2, 2, 1, "final", 0)
pymysql.install_as_MySQLdb()
```

---

## Environment-Specific Setup

### Development:
```env
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOW_ALL_ORIGINS=True
```

### Production:
```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=generate-strong-secret-key
CORS_ALLOW_ALL_ORIGINS=False
```

---

## Next Steps

After successful installation:

1. ✅ Login to admin panel
2. ✅ Create a test product (barcode auto-generates!)
3. ✅ Process a test sale
4. ✅ View dashboard statistics
5. ✅ Check reports
6. ✅ Test API endpoints

---

## Additional Configuration

### Email Settings (Optional):
```python
# In settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

### Logging (Optional):
Already configured in settings.py. Logs go to `logs/` folder.

---

## Verification Checklist

- [ ] Python installed and version verified
- [ ] MySQL installed and running
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] Database created
- [ ] Migrations completed
- [ ] Superuser created
- [ ] Sample data loaded
- [ ] Server starts without errors
- [ ] Can access frontend
- [ ] Can login
- [ ] Can create product with auto-barcode
- [ ] API endpoints working

---

**Installation Complete!** 🎉

For more help, see:
- API Documentation: `docs/API_DOCUMENTATION.md`
- User Guide: `docs/USER_GUIDE.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`
