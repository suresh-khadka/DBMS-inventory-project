# 🗄️ SQL Database Support Guide

Your Django Inventory Management System has **complete SQL database support** with both **MySQL** and **PostgreSQL** compatibility!

---

## ✅ Database Support Status

| Database | Status | Tier | Use Case |
|----------|--------|------|----------|
| **MySQL 8.0+** | ✅ Full Support | Production | Traditional deployments |
| **PostgreSQL 13+** | ✅ Full Support | Production | Render.com (recommended) |
| **SQLite** | ✅ Works | Development | Local testing only |

---

## 📊 Database Models (9 Tables)

Your system includes 9 complete Django models:

### 1. **User Model** 👤
```python
- username (CharField, unique)
- password (hashed)
- role (admin, employee, customer)
- email (optional)
- phone (optional)
- is_active (boolean)
- created_at, last_login_date
```
**Database Table:** `users`
**Primary Key:** `id`
**Indexes:** username, role

### 2. **Employee Model** 👨‍💼
```python
- employee_name (CharField)
- email (unique)
- phone (optional)
- role (admin, worker)
- salary (decimal)
- hire_date (date)
- is_active (boolean)
- created_at, updated_at
```
**Database Table:** `employees`
**Foreign Key:** user_id → users(id)
**Indexes:** email, is_active

### 3. **Customer Model** 🛍️
```python
- customer_name (CharField)
- email (unique)
- phone (optional)
- address (text)
- total_purchases (count)
- total_spent (decimal)
- created_at, updated_at
```
**Database Table:** `customers`
**Foreign Key:** user_id → users(id)
**Indexes:** email

### 4. **Product Model** 📦
```python
- barcode (CharField, primary key) ⭐ AUTO-GENERATED
- product_name (CharField)
- description (text)
- cost_price (decimal)
- selling_price (decimal)
- discount_price (decimal, optional)
- discount_percentage (decimal)
- stock_level (integer)
- min_stock_level (integer)
- category (CharField)
- supplier (CharField)
- total_sales_count (integer)
- total_revenue (decimal)
- is_active (boolean)
- created_at, updated_at
```
**Database Table:** `products`
**Primary Key:** barcode
**Indexes:** product_name, category, is_active, stock_level

### 5. **Sale Model** 💰
```python
- barcode (ForeignKey → Product)
- customer (ForeignKey → Customer, optional)
- quantity_sold (integer)
- unit_price (decimal)
- total_amount (decimal)
- sale_date (datetime)
- processed_by (ForeignKey → Employee, optional)
- payment_method (cash, card, online)
- discount_applied (boolean)
- discount_amount (decimal)
```
**Database Table:** `sales`
**Foreign Keys:** barcode, customer_id, processed_by
**Indexes:** sale_date, barcode

### 6. **PurchaseHistory Model** 📋
```python
- customer (ForeignKey → Customer)
- sale (ForeignKey → Sale)
- purchase_date (datetime)
```
**Database Table:** `purchase_history`
**Foreign Keys:** customer_id, sale_id
**Indexes:** customer_id, purchase_date

### 7. **InventoryLog Model** 📝
```python
- barcode (ForeignKey → Product)
- action (add, update, delete, sale, restock, adjustment)
- quantity_changed (integer)
- previous_stock (integer)
- new_stock (integer)
- performed_by (ForeignKey → User)
- timestamp (datetime)
- notes (text)
```
**Database Table:** `inventory_logs`
**Foreign Keys:** barcode, performed_by
**Indexes:** barcode, timestamp

### 8. **Expense Model** 💸
```python
- expense_type (product_cost, employee_salary, rent, utilities, marketing, maintenance, other)
- description (text)
- amount (decimal)
- expense_date (date)
- recorded_by (ForeignKey → Employee)
- product (ForeignKey → Product, optional)
- employee (ForeignKey → Employee, optional)
- created_at (datetime)
```
**Database Table:** `expenses`
**Foreign Keys:** recorded_by, product (optional), employee (optional)
**Indexes:** expense_date, expense_type

### 9. **Alert Model** ⚠️
```python
- alert_type (low_stock, out_of_stock, system)
- message (text)
- barcode (ForeignKey → Product, optional)
- severity (low, medium, high)
- is_read (boolean)
- created_at (datetime)
```
**Database Table:** `alerts`
**Foreign Key:** barcode (optional)
**Indexes:** is_read, created_at

---

## 🔧 Database Configuration

### MySQL (Local Development)

#### Connection Settings
```python
# In .env file:
DB_ENGINE=django.db.backends.mysql
DB_NAME=inventory_db
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306
```

#### Installation
```bash
# Install MySQL
# Windows: Download from mysql.com
# Mac: brew install mysql
# Linux: sudo apt-get install mysql-server

# Create database
mysql -u root -p
CREATE DATABASE inventory_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

#### Python Dependencies
```bash
pip install PyMySQL==1.1.0
# OR
pip install mysqlclient
```

---

### PostgreSQL (Production - Render)

#### Connection Settings
```python
# In .env file (Render auto-sets this):
DATABASE_URL=postgresql://user:password@host:5432/inventory_db
```

#### Installation
```bash
# Render auto-provisions PostgreSQL 15
# No manual installation needed!

# Local testing (optional):
# Mac: brew install postgresql
# Linux: sudo apt-get install postgresql
# Windows: Download from postgresql.org
```

#### Python Dependencies
```bash
pip install psycopg2-binary==2.9.9
# Already in requirements.txt
```

---

## 🚀 Database Initialization

### Method 1: Django Migrations (Recommended)
```bash
# Create migration files
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# View migration status
python manage.py migrate --plan

# Check database
python manage.py dbshell
```

### Method 2: Manual SQL Schema
```bash
# Import schema file
mysql -u root -p inventory_db < database/schema.sql
```

### Method 3: Load Sample Data
```bash
# Create admin and sample data
python manage.py create_sample_data

# Creates:
# - Admin user (admin/admin123)
# - Worker user (worker1/worker123)
# - Customer user (customer1/customer123)
# - 10 sample products
# - 5 sample sales
```

---

## 📝 SQL Queries (Common Operations)

### User Management
```sql
-- Get all users
SELECT * FROM users;

-- Get active users by role
SELECT * FROM users WHERE is_active = 1 AND role = 'admin';

-- Count users by role
SELECT role, COUNT(*) as count FROM users GROUP BY role;
```

### Product Management
```sql
-- Get all products
SELECT * FROM products WHERE is_active = 1;

-- Search products by name
SELECT * FROM products WHERE product_name LIKE '%wireless%';

-- Get low stock products
SELECT * FROM products WHERE stock_level <= min_stock_level;

-- Get out of stock products
SELECT * FROM products WHERE stock_level = 0;

-- Top 10 best sellers
SELECT product_name, barcode, total_sales_count, total_revenue 
FROM products 
ORDER BY total_sales_count DESC 
LIMIT 10;
```

### Sales Analysis
```sql
-- Total sales today
SELECT COUNT(*) as total_sales, SUM(total_amount) as total_revenue
FROM sales 
WHERE DATE(sale_date) = CURDATE();

-- Sales by payment method
SELECT payment_method, COUNT(*) as count, SUM(total_amount) as total
FROM sales
GROUP BY payment_method;

-- Top customers
SELECT customer_name, COUNT(*) as purchases, SUM(total_amount) as spent
FROM customers
LEFT JOIN sales ON customers.id = sales.customer_id
GROUP BY customer_name
ORDER BY spent DESC
LIMIT 10;
```

### Financial Reports
```sql
-- Monthly revenue
SELECT DATE_FORMAT(sale_date, '%Y-%m') as month, SUM(total_amount) as revenue
FROM sales
GROUP BY DATE_FORMAT(sale_date, '%Y-%m')
ORDER BY month DESC;

-- Monthly expenses
SELECT DATE_FORMAT(expense_date, '%Y-%m') as month, expense_type, SUM(amount) as total
FROM expenses
GROUP BY DATE_FORMAT(expense_date, '%Y-%m'), expense_type
ORDER BY month DESC;

-- Profit/Loss calculation
SELECT 
  DATE_FORMAT(s.sale_date, '%Y-%m') as month,
  SUM(s.total_amount) as revenue,
  SUM(s.total_amount - (p.cost_price * s.quantity_sold)) as profit,
  (SUM(s.total_amount - (p.cost_price * s.quantity_sold)) / SUM(s.total_amount) * 100) as margin_percent
FROM sales s
JOIN products p ON s.barcode = p.barcode
GROUP BY DATE_FORMAT(s.sale_date, '%Y-%m');
```

### Inventory Tracking
```sql
-- Inventory history for product
SELECT * FROM inventory_logs 
WHERE barcode = 'WIRELESSMO1234'
ORDER BY timestamp DESC;

-- Last 100 inventory changes
SELECT il.*, u.username, p.product_name
FROM inventory_logs il
LEFT JOIN users u ON il.performed_by = u.id
LEFT JOIN products p ON il.barcode = p.barcode
ORDER BY il.timestamp DESC
LIMIT 100;

-- Stock value calculation
SELECT 
  product_name, 
  barcode, 
  stock_level, 
  cost_price,
  (stock_level * cost_price) as inventory_value
FROM products
WHERE is_active = 1
ORDER BY inventory_value DESC;
```

---

## 🔐 Database Security

### Best Practices ✅

1. **Use Environment Variables**
   ```python
   # GOOD ✅
   DB_PASSWORD = os.getenv('DB_PASSWORD')
   
   # BAD ❌
   DB_PASSWORD = 'hardcoded_password'
   ```

2. **Least Privilege Accounts**
   ```sql
   -- Create limited user for app
   CREATE USER 'inventory_app'@'localhost' IDENTIFIED BY 'strong_password';
   GRANT SELECT, INSERT, UPDATE, DELETE ON inventory_db.* TO 'inventory_app'@'localhost';
   ```

3. **Connection Encryption**
   ```python
   # PostgreSQL SSL
   'OPTIONS': {
       'sslmode': 'require',
   }
   ```

4. **SQL Injection Prevention**
   ```python
   # GOOD - Django ORM (parameterized)
   Product.objects.filter(product_name__icontains=search_term)
   
   # BAD - Raw SQL (vulnerable)
   Product.objects.raw(f"SELECT * FROM products WHERE name = '{search_term}'")
   ```

5. **Backup Strategy**
   ```bash
   # MySQL backup
   mysqldump -u root -p inventory_db > backup.sql
   
   # PostgreSQL backup
   pg_dump inventory_db > backup.sql
   
   # Restore
   mysql -u root -p inventory_db < backup.sql
   psql inventory_db < backup.sql
   ```

---

## 📊 Database Performance

### Indexes (Already Configured) ⚡

```sql
-- Users table
INDEX idx_username (username)
INDEX idx_role (role)

-- Employees table
INDEX idx_email (email)
INDEX idx_active (is_active)

-- Customers table
INDEX idx_email (email)

-- Products table
INDEX idx_product_name (product_name)
INDEX idx_category (category)
INDEX idx_active (is_active)
INDEX idx_stock (stock_level)

-- Sales table
INDEX idx_sale_date (sale_date)
INDEX idx_barcode (barcode)

-- Inventory Logs table
INDEX idx_barcode (barcode)
INDEX idx_timestamp (timestamp)

-- Expenses table
INDEX idx_expense_date (expense_date)
INDEX idx_expense_type (expense_type)

-- Alerts table
INDEX idx_is_read (is_read)
INDEX idx_created_at (created_at)
```

### Query Optimization Tips

1. **Use SELECT with specific columns**
   ```sql
   -- GOOD
   SELECT barcode, product_name, stock_level FROM products;
   
   -- Slow
   SELECT * FROM products;
   ```

2. **Filter early**
   ```sql
   -- GOOD
   SELECT * FROM sales WHERE YEAR(sale_date) = 2024 AND total_amount > 1000;
   
   -- Slow
   SELECT * FROM sales WHERE total_amount > 1000;
   ```

3. **Use LIMIT for large queries**
   ```sql
   SELECT * FROM inventory_logs ORDER BY timestamp DESC LIMIT 100;
   ```

4. **Batch operations**
   ```python
   # Bulk insert
   Product.objects.bulk_create([product1, product2, product3])
   
   # Bulk update
   Product.objects.bulk_update(products, ['stock_level'], batch_size=100)
   ```

---

## 🔧 Database Maintenance

### Regular Tasks

```bash
# Weekly: Check for errors
python manage.py check

# Monthly: Optimize tables (MySQL)
mysql -u root -p inventory_db -e "OPTIMIZE TABLE products, sales, customers;"

# Monthly: Analyze tables (PostgreSQL)
psql inventory_db -c "ANALYZE;"

# Quarterly: Backup
mysqldump -u root -p inventory_db > backup_$(date +%Y%m%d).sql

# Yearly: Update statistics
python manage.py optimize_db  # If using django-extensions
```

### Monitor Connections
```sql
-- MySQL active connections
SHOW PROCESSLIST;

-- PostgreSQL active connections
SELECT pid, usename, application_name, state FROM pg_stat_activity;
```

---

## 🚀 Database Migration in Production

### Render Deployment Process

1. **Build Phase** - Migrations run automatically
   ```bash
   python manage.py migrate --noinput
   ```

2. **Verify Migrations**
   ```bash
   python manage.py migrate --plan
   ```

3. **Rollback if needed**
   ```bash
   python manage.py migrate app_name 0001_initial
   ```

---

## 📚 Database Documentation Files

| File | Purpose |
|------|---------|
| `database/schema.sql` | Complete SQL schema for MySQL |
| `backend/inventory/models.py` | Django models (ORM definition) |
| `docs/API_DOCUMENTATION.md` | API endpoints (uses database) |

---

## ✅ Database Checklist

Before deployment, verify:

- [ ] Database created and accessible
- [ ] All migrations applied: `python manage.py migrate`
- [ ] Database user has proper permissions
- [ ] Backups configured
- [ ] Connection pool settings optimized
- [ ] Indexes created
- [ ] Sample data loaded (if testing)
- [ ] Test queries working
- [ ] Environment variables set
- [ ] SSL/TLS configured (production)

---

## 🆘 Troubleshooting

### Connection Error
```
Error: "can't connect to MySQL server"
```
**Solution:**
1. Verify MySQL is running: `mysql -u root -p`
2. Check credentials in .env
3. Verify host/port: `telnet localhost 3306`

### Migration Error
```
Error: "migration not applied"
```
**Solution:**
1. Check status: `python manage.py migrate --plan`
2. Rollback: `python manage.py migrate app 0001`
3. Reapply: `python manage.py migrate`

### Permission Error
```
Error: "Access denied for user"
```
**Solution:**
1. Check database user permissions
2. Grant access: `GRANT ALL ON inventory_db.* TO 'user'@'localhost';`
3. Flush privileges: `FLUSH PRIVILEGES;`

### Slow Queries
```
Timeout or slow response
```
**Solution:**
1. Add indexes: `CREATE INDEX idx_name ON table(column);`
2. Optimize tables: `OPTIMIZE TABLE table_name;`
3. Check query: `EXPLAIN SELECT ...`

---

## 📊 Database Statistics

| Metric | Value |
|--------|-------|
| **Tables** | 9 complete models |
| **Foreign Keys** | 12+ relationships |
| **Indexes** | 20+ optimized indexes |
| **Character Set** | utf8mb4 (full Unicode) |
| **Engine** | InnoDB (MySQL) / Default (PostgreSQL) |
| **Max Connections** | 5 (Free) / Unlimited (Pro) |

---

## 🎉 Your Database is Ready!

✅ **Complete SQL Support** with:
- ✅ 9 fully defined models
- ✅ MySQL & PostgreSQL compatibility
- ✅ Optimized indexes
- ✅ Foreign key relationships
- ✅ Auto-generated barcode system
- ✅ Audit logging
- ✅ Sample data scripts
- ✅ Security best practices

---

## 📖 Quick Reference

**Create database:**
```bash
python manage.py migrate
```

**Create sample data:**
```bash
python manage.py create_sample_data
```

**Access database shell:**
```bash
python manage.py dbshell
```

**Create superuser:**
```bash
python manage.py createsuperuser
```

**Backup database:**
```bash
mysqldump -u root -p inventory_db > backup.sql
```

---

**Status:** ✅ FULL SQL SUPPORT ENABLED
**Ready to use:** YES ✅
