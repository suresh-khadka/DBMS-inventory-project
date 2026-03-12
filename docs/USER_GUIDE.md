# User Guide

## Django Inventory Management System

---

## Getting Started

### Login
1. Open http://localhost:8000
2. Enter credentials
3. Click "Login"

**Default accounts:**
- Admin: admin / admin123
- Worker: worker1 / worker123
- Customer: customer1 / customer123

---

## Dashboard

View key metrics:
- Total products
- Low stock items
- Today's sales
- Monthly revenue
- Recent sales
- Low stock alerts

---

## Product Management

### View Products
1. Click "Products" in sidebar
2. See all products with barcodes
3. Filter and search

### Create Product
1. Click "Add New Product"
2. Enter product details:
   - Product name (required)
   - Description
   - Cost price (required)
   - Selling price (required)
   - Stock level
   - Min stock level
   - Category
   - Supplier
3. Click "Create Product"
4. **Barcode is automatically generated!**

**Example:**
```
Product Name: Wireless Mouse
Auto-Generated Barcode: WIRELESSMO1234
```

### Edit Product
1. Click "Edit" on product row
2. Modify details
3. Click "Update"

### Delete Product
1. Click "Delete" on product row
2. Confirm deletion

---

## Sales Processing

### Create Sale
1. Click "Sales" in sidebar
2. Click "New Sale"
3. Select product (shows barcode)
4. Enter quantity
5. Select payment method
6. Click "Process Sale"
7. **Stock is automatically updated!**

### View Sales History
1. Click "Sales"
2. See all transactions
3. Filter by date

---

## Reports

### Profit/Loss Report
- View revenue
- View expenses
- See profit
- Check profit margin

### Inventory Report
- Total products
- Total inventory value
- Low stock count

### Sales Trend
- 7-day sales trend
- Revenue by day

---

## Alerts

### View Alerts
1. Click "Alerts" (shows unread count)
2. See all system notifications
3. Click to mark as read

**Alert Types:**
- Low stock warnings
- Out of stock alerts
- System notifications

---

## Admin Panel

### Access
1. Go to http://localhost:8000/admin
2. Login with admin credentials
3. Manage all data

### Features:
- User management
- Employee management
- Customer management
- Product management (view barcodes!)
- Sales records
- Inventory logs
- Expenses
- Alerts

---

## Tips

### Auto-Generated Barcodes
- Created automatically
- Based on product name
- Always unique
- Used throughout system
- Displayed in product list

### Stock Management
- Stock updates on sale
- Alerts when low
- Track all changes

### Search & Filter
- Search products by name
- Filter by category
- Sort by any column

---

## Troubleshooting

### Can't login?
- Check username/password
- Try default credentials
- Contact administrator

### Barcode not showing?
- Check product was created
- Refresh page
- Check browser console

### Stock not updating?
- Check sale was processed
- View inventory logs
- Check permissions

---

**For more help, contact system administrator**
