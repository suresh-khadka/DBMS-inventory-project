# API Documentation

## Django Inventory Management System - REST API Reference

Base URL: `http://localhost:8000/api`

---

## Authentication

### Login
**Endpoint:** `POST /api/auth/login/`

**Request:**
```json
{
    "username": "admin",
    "password": "admin123"
}
```

**Response:**
```json
{
    "success": true,
    "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
        "id": 1,
        "username": "admin",
        "role": "admin"
    }
}
```

---

## Products

### List Products
**Endpoint:** `GET /api/products/`

**Response:**
```json
{
    "success": true,
    "data": [
        {
            "barcode": "WIRELESSMO1234",
            "product_name": "Wireless Mouse",
            "description": "Ergonomic wireless mouse",
            "cost_price": "15.00",
            "selling_price": "25.00",
            "stock_level": 50,
            "min_stock_level": 10,
            "category": "Electronics",
            "supplier": "TechCorp",
            "is_active": true,
            "profit_margin": 66.67,
            "stock_status": "in_stock"
        }
    ]
}
```

### Create Product (AUTO-BARCODE!)
**Endpoint:** `POST /api/products/create/`

**Request:**
```json
{
    "product_name": "Laptop Dell XPS",
    "description": "High performance laptop",
    "cost_price": "1200.00",
    "selling_price": "1500.00",
    "stock_level": 10,
    "min_stock_level": 5,
    "category": "Computers",
    "supplier": "Dell Inc"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Product created successfully",
    "data": {
        "barcode": "LAPTOPDELL5678",
        "product_name": "Laptop Dell XPS"
    }
}
```

### Get Product by Barcode
**Endpoint:** `GET /api/products/<barcode>/`

**Example:** `GET /api/products/WIRELESSMO1234/`

### Update Product
**Endpoint:** `PUT /api/products/<barcode>/update/`

**Request:**
```json
{
    "stock_level": 75,
    "selling_price": "27.00"
}
```

### Delete Product
**Endpoint:** `DELETE /api/products/<barcode>/delete/`

### Get Low Stock Products
**Endpoint:** `GET /api/products/low-stock/`

---

## Sales

### List Sales
**Endpoint:** `GET /api/sales/`

**Query Parameters:**
- `limit` (optional): Number of results (default: 50)

**Example:** `GET /api/sales/?limit=10`

### Create Sale
**Endpoint:** `POST /api/sales/create/`

**Request:**
```json
{
    "barcode": "WIRELESSMO1234",
    "quantity_sold": 2,
    "unit_price": "25.00",
    "payment_method": "cash",
    "customer": 1
}
```

**Response:**
```json
{
    "success": true,
    "message": "Sale created successfully",
    "data": {
        "id": 5,
        "barcode": "WIRELESSMO1234",
        "total_amount": "50.00"
    }
}
```

### Get Sale Details
**Endpoint:** `GET /api/sales/<id>/`

---

## Dashboard

### Get Dashboard Stats
**Endpoint:** `GET /api/dashboard/stats/`

**Response:**
```json
{
    "success": true,
    "data": {
        "products": {
            "total": 25,
            "lowStock": 3
        },
        "sales": {
            "today": {
                "totalSales": 5,
                "totalRevenue": 150.00
            },
            "thisMonth": {
                "totalSales": 48,
                "totalRevenue": 2340.00
            }
        },
        "employees": 5,
        "customers": 12,
        "unreadAlerts": 2
    }
}
```

---

## Employees

### List Employees
**Endpoint:** `GET /api/employees/`

### Create Employee
**Endpoint:** `POST /api/employees/create/`

**Request:**
```json
{
    "employee_name": "John Doe",
    "email": "john@example.com",
    "phone": "1234567890",
    "role": "worker",
    "salary": "3000.00",
    "hire_date": "2024-01-15"
}
```

### Update Employee
**Endpoint:** `PUT /api/employees/<id>/update/`

### Delete Employee
**Endpoint:** `DELETE /api/employees/<id>/delete/`

---

## Customers

### List Customers
**Endpoint:** `GET /api/customers/`

### Create Customer
**Endpoint:** `POST /api/customers/create/`

**Request:**
```json
{
    "customer_name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "0987654321",
    "address": "123 Main St, City"
}
```

### Get Customer Purchase History
**Endpoint:** `GET /api/customers/<id>/purchases/`

---

## Reports

### Profit/Loss Report
**Endpoint:** `GET /api/reports/profit-loss/`

**Response:**
```json
{
    "success": true,
    "data": {
        "revenue": 2500.00,
        "expenses": 800.00,
        "profit": 1700.00,
        "profitMargin": 68.00
    }
}
```

### Inventory Report
**Endpoint:** `GET /api/reports/inventory/`

**Response:**
```json
{
    "success": true,
    "data": {
        "totalProducts": 25,
        "totalValue": 45000.00,
        "lowStock": 3
    }
}
```

### Sales Trend (7 days)
**Endpoint:** `GET /api/reports/sales-trend/`

---

## Expenses

### List Expenses
**Endpoint:** `GET /api/expenses/`

### Create Expense
**Endpoint:** `POST /api/expenses/create/`

**Request:**
```json
{
    "expense_type": "Utilities",
    "description": "Monthly electricity bill",
    "amount": "150.00",
    "expense_date": "2024-03-01"
}
```

---

## Alerts

### List Alerts
**Endpoint:** `GET /api/alerts/`

### Mark Alert as Read
**Endpoint:** `PUT /api/alerts/<id>/read/`

---

## Error Responses

### 400 Bad Request
```json
{
    "success": false,
    "errors": {
        "product_name": ["This field is required."]
    }
}
```

### 401 Unauthorized
```json
{
    "success": false,
    "error": "Invalid credentials"
}
```

### 404 Not Found
```json
{
    "success": false,
    "error": "Product not found"
}
```

---

## Rate Limiting

Currently no rate limiting. Will be added in production.

---

## Pagination

Default page size: 50 items

---

## Complete Endpoint List

### Authentication (3):
- POST /api/auth/login/
- POST /api/auth/logout/
- GET /api/auth/me/

### Products (6):
- GET /api/products/
- POST /api/products/create/
- GET /api/products/<barcode>/
- PUT /api/products/<barcode>/update/
- DELETE /api/products/<barcode>/delete/
- GET /api/products/low-stock/

### Sales (3):
- GET /api/sales/
- POST /api/sales/create/
- GET /api/sales/<id>/

### Employees (5):
- GET /api/employees/
- POST /api/employees/create/
- GET /api/employees/<id>/
- PUT /api/employees/<id>/update/
- DELETE /api/employees/<id>/delete/

### Customers (6):
- GET /api/customers/
- POST /api/customers/create/
- GET /api/customers/<id>/
- PUT /api/customers/<id>/update/
- DELETE /api/customers/<id>/delete/
- GET /api/customers/<id>/purchases/

### Expenses (4):
- GET /api/expenses/
- POST /api/expenses/create/
- GET /api/expenses/<id>/
- GET /api/expenses/summary/

### Reports (3):
- GET /api/reports/profit-loss/
- GET /api/reports/inventory/
- GET /api/reports/sales-trend/

### Dashboard (1):
- GET /api/dashboard/stats/

### Alerts (2):
- GET /api/alerts/
- PUT /api/alerts/<id>/read/

### Inventory Logs (1):
- GET /api/inventory-logs/

**Total: 40+ Endpoints**

---

## Testing with cURL

### Login:
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Create Product:
```bash
curl -X POST http://localhost:8000/api/products/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Test Product",
    "cost_price": "10.00",
    "selling_price": "15.00",
    "stock_level": 50
  }'
```

### List Products:
```bash
curl http://localhost:8000/api/products/
```

---

**API Documentation Complete!** 🎉
