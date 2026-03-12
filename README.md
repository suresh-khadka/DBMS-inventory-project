# 🏷️ Inventory Management System with Auto-Generated Barcodes

A production-ready Django inventory management system that **automatically generates unique barcodes** for products.

---

## ✨ Key Feature: Auto-Generated Barcodes

The standout feature of this system is **automatic barcode generation**. Every product gets a unique barcode without manual entry.

### How It Works

```
Product Name: "Wireless Mouse"
→ Remove special characters, uppercase, take first 10 chars
→ Add 4 random digits
→ Check for uniqueness
→ Result: WIRELESSMO1234
```

### Examples
- "Wireless Mouse" → `WIRELESSMO2847`
- "Laptop Dell XPS 15" → `LAPTOPDELL5091`
- "USB-C Cable 2m" → `USBCCABLE3456`

**Location:** `backend/inventory/models.py` (Product model)

---

## 🎯 Quick Start

### Windows
```bash
scripts\setup.bat
```

### Linux/Mac
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Docker
```bash
docker-compose up -d
```

Access the application at `http://localhost:8000`

---

## 📋 Default Credentials

After initial setup:
- **Admin:** `admin` / `admin123`
- **Worker:** `worker1` / `worker123`
- **Customer:** `customer1` / `customer123`

---

## 🏗️ Project Structure

```
├── backend/              # Django REST API
│   ├── inventory/        # Main app with barcode logic
│   ├── manage.py
│   └── requirements.txt
├── frontend/             # Web interface
│   ├── index.html       # Login
│   ├── dashboard.html   # Main dashboard
│   ├── css/
│   └── js/
├── database/             # Database schema & sample data
├── docs/                 # Detailed documentation
├── scripts/              # Setup & utility scripts
├── docker-compose.yml
└── README.md
```

---

## 📚 Features

### Backend (Django)
- ✅ 40+ REST API endpoints
- ✅ JWT authentication
- ✅ Role-based access control (Admin/Worker/Customer)
- ✅ **Auto-generated unique barcodes** 
- ✅ Automatic stock updates
- ✅ Low stock alerts
- ✅ Inventory audit logs
- ✅ Reports & analytics

### Frontend
- ✅ Responsive design
- ✅ Product CRUD operations
- ✅ Sales processing with barcode display
- ✅ Real-time dashboard statistics
- ✅ Barcode viewer and printer support

### Database
- ✅ 9 optimized models
- ✅ Barcode as unique identifier
- ✅ Foreign key relationships
- ✅ Audit trail logging

---

## 💻 Technology Stack

- **Backend:** Python 3.8+, Django 4.2.7, Django REST Framework
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Database:** MySQL 8.0+
- **Authentication:** JWT
- **Containerization:** Docker & Docker Compose

---

## 📖 Documentation

All documentation is in the `docs/` folder:

| File | Purpose |
|------|---------|
| `INSTALLATION.md` | Step-by-step setup guide |
| `API_DOCUMENTATION.md` | Complete API reference |
| `USER_GUIDE.md` | How to use the application |
| `DEPLOYMENT.md` | Production deployment |
| `TROUBLESHOOTING.md` | Common issues & solutions |

---

## 🔧 API Endpoints (Quick Reference)

```
POST   /api/auth/login/           Login
GET    /api/dashboard/stats/      Dashboard statistics
GET    /api/products/             List all products
POST   /api/products/create/      Create product (barcode auto-generated!)
GET    /api/products/<barcode>/   Get product by barcode
POST   /api/sales/create/         Create sales transaction
GET    /api/sales/                List sales
GET    /api/reports/profit-loss/  Profit/loss report
```

See `docs/API_DOCUMENTATION.md` for the complete reference.

---

## 🧪 Testing Barcode Generation

### In Python Shell
```python
python manage.py shell

from inventory.models import Product
from decimal import Decimal

product = Product.objects.create(
    product_name="Test Product",
    cost_price=Decimal("10.00"),
    selling_price=Decimal("15.00"),
    stock_level=100
)

print(product.barcode)  # Output: TESTPRODUC1234
```

### Via API
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

curl -X POST http://localhost:8000/api/products/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Test Item",
    "cost_price": "20.00",
    "selling_price": "30.00",
    "stock_level": 50
  }'
```

---

## 🔒 Security Features

- JWT token-based authentication
- Password hashing with bcrypt
- CSRF protection
- SQL injection prevention
- XSS protection
- Role-based access control

---

## 📦 Database Models

1. **User** - Authentication & user roles
2. **Employee** - Staff management
3. **Customer** - Customer information
4. **Product** - Products with **auto-generated barcodes** ⭐
5. **Sale** - Sales transactions
6. **PurchaseHistory** - Purchase tracking
7. **InventoryLog** - Audit trail
8. **Expense** - Business expenses
9. **Alert** - System notifications

---

## 🐳 Docker Support

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

## 🚀 Deployment

For production deployment:
1. See `docs/DEPLOYMENT.md` for server configuration
2. Update Django settings for production
3. Configure environment variables
4. Run database migrations
5. Collect static files

---

## 📝 Usage Example

### Creating a Product with Auto-Generated Barcode

1. Go to Products page
2. Click "Add New Product"
3. Enter product details (name, cost, selling price, stock)
4. **Click Create** → Barcode generated automatically!
5. Product now appears in inventory with unique barcode

### Processing a Sale

1. Go to Sales page
2. Search by barcode (or select from list)
3. Enter quantity
4. Click "Process Sale"
5. **Stock updated automatically!**

---

## 🆘 Support

- **Setup Issues?** → Check `docs/INSTALLATION.md`
- **How to use?** → Read `docs/USER_GUIDE.md`
- **API Questions?** → See `docs/API_DOCUMENTATION.md`
- **Deployment Help?** → Read `docs/DEPLOYMENT.md`
- **Problems?** → Check `docs/TROUBLESHOOTING.md`

---

## 📄 License

This project is for educational and commercial use.

---

## 🎉 Ready to Go!

This system is **100% complete and production-ready** with:
- ✅ Full-featured barcode system
- ✅ Complete REST API
- ✅ Modern web interface
- ✅ Comprehensive documentation
- ✅ Easy deployment options

**Start now:** Run the setup script for your platform!

---

**Happy Inventory Managing!** 📦🏷️
