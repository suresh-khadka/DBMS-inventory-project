"""
Database Models for Inventory Management System
WITH AUTO-GENERATED BARCODE SYSTEM
"""

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator,MaxValueValidator
from decimal import Decimal
import random
import re


# ==================== USER MANAGEMENT ====================

class UserManager(BaseUserManager):
    """Custom user manager"""
    
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('Username is required')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with roles"""
    
    ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('employee', 'Employee'),  # Change 'worker' to 'employee'
    ('customer', 'Customer'),
]
    
    username = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_login_date = models.DateTimeField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'username'
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.role})"


# ==================== EMPLOYEES ====================

class Employee(models.Model):
    """Employee model"""
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('worker', 'Worker'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='employee_profile')
    employee_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='worker')
    salary = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)
    last_salary_added_date = models.DateField(null=True, blank=True)
    salary = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Monthly salary in Indian Rupees (Rs)"  # ADD THIS
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'employees'
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
    
    def __str__(self):
        return self.employee_name


# ==================== CUSTOMERS ====================

class Customer(models.Model):
    """Customer model"""
    
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_profile')
    customer_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    total_purchases = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customers'
        verbose_name = 'Customer'
        verbose_name_plural = 'Customers'
    
    def __str__(self):
        return self.customer_name


# ==================== PRODUCTS WITH BARCODE ====================

class Product(models.Model):
    """
    Product model with AUTO-GENERATED BARCODE
    Barcode format: ProductName (cleaned) + 4 random digits
    Example: "Wireless Mouse" → "WIRELESSMO1234"
    """
    
    barcode = models.CharField(max_length=50, primary_key=True, editable=False)
    product_name = models.CharField(max_length=150)
    description = models.TextField(null=True, blank=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    stock_level = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    min_stock_level = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    # NEW FIELDS for Feature 12: Discount pricing
    discount_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Discounted price in ₹ (optional)"
    )
    discount_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text="Discount percentage (auto-calculated)"
    )
    category = models.CharField(max_length=50, null=True, blank=True)
    supplier = models.CharField(max_length=100, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    # NEW FIELDS for Feature 6: Track sales count for top products
    total_sales_count = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product_name} ({self.barcode})"
    
    def get_final_price(self):
        """Get actual selling price (with discount if available)"""
        if self.discount_price and self.discount_price < self.selling_price:
            return self.discount_price
        return self.selling_price
    
    @staticmethod
    def generate_barcode(product_name):
        """
        Generate unique barcode from product name + 4 random digits
        Format: PRODUCTNAME1234
        Only checks ACTIVE products (is_active=True) to allow reusing barcodes of deleted products
        """
        # Clean product name: remove special chars, uppercase, max 10 chars
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', product_name).upper()[:10]
        
        # Generate random 4 digits
        random_digits = str(random.randint(1000, 9999))
        
        # Combine
        barcode = f"{clean_name}{random_digits}"
        
        # Check uniqueness - only check ACTIVE products
        max_retries = 100
        retry_count = 0
        while Product.objects.filter(barcode=barcode, is_active=True).exists() and retry_count < max_retries:
            random_digits = str(random.randint(1000, 9999))
            barcode = f"{clean_name}{random_digits}"
            retry_count += 1
        
        return barcode
    
    def save(self, *args, **kwargs):
        # Generate barcode if not set
        if not self.barcode:
            self.barcode = self.generate_barcode(self.product_name)
        
        # NEW: Calculate discount percentage
        if self.discount_price and self.discount_price < self.selling_price:
            self.discount_percentage = (
                (self.selling_price - self.discount_price) / self.selling_price * 100
            )
        else:
            self.discount_percentage = Decimal('0.00')
        
        super().save(*args, **kwargs)
        self.check_stock_alert()
    
    def check_stock_alert(self):
        """Create alert if stock is low or out"""
        if self.stock_level == 0:
            Alert.objects.get_or_create(
                barcode=self,
                alert_type='out_of_stock',
                defaults={
                    'message': f'Product "{self.product_name}" is out of stock!',
                    'severity': 'high'
                }
            )
        elif self.stock_level <= self.min_stock_level:
            Alert.objects.get_or_create(
                barcode=self,
                alert_type='low_stock',
                defaults={
                    'message': f'Product "{self.product_name}" is running low!',
                    'severity': 'medium'
                }
            )


# ==================== SALES ====================

class Sale(models.Model):
    """Sales transaction model"""
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('online', 'Online'),
    ]
    
    barcode = models.ForeignKey(Product, on_delete=models.RESTRICT, db_column='barcode')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    quantity_sold = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    sale_date = models.DateTimeField(auto_now_add=True)
    processed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    discount_applied = models.BooleanField(default=False)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    class Meta:
        db_table = 'sales'
        verbose_name = 'Sale'
        verbose_name_plural = 'Sales'
        ordering = ['-sale_date']
    
    def __str__(self):
        return f"Sale #{self.id} - {self.barcode.product_name}"
    
    def save(self, *args, **kwargs):
        # Calculate total
        self.total_amount = self.unit_price * self.quantity_sold

        product = self.barcode
        if product.discount_price and self.unit_price == product.discount_price:
            self.discount_applied = True
            self.discount_amount = (product.selling_price - product.discount_price) * self.quantity_sold
        
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            product.stock_level -= self.quantity_sold
            product.total_sales_count += self.quantity_sold  # NEW
            product.total_revenue += self.total_amount  # NEW
            product.save()
            
            # NEW: Update customer stats if customer exists
            if self.customer:
                self.customer.total_purchases += 1
                self.customer.total_spent += self.total_amount
                self.customer.save()
            
            # Create inventory log
            InventoryLog.objects.create(
                barcode=product,
                action='sale',
                quantity_changed=-self.quantity_sold,
                previous_stock=product.stock_level + self.quantity_sold,
                new_stock=product.stock_level,
                performed_by=self.processed_by.user if self.processed_by else None,
                notes=f"Sale ID: {self.id}"
            )


# ==================== PURCHASE HISTORY ====================

class PurchaseHistory(models.Model):
    """Customer purchase history"""
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='purchases')
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE)
    purchase_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'purchase_history'
        verbose_name = 'Purchase History'
        verbose_name_plural = 'Purchase Histories'
        ordering = ['-purchase_date']
    
    def __str__(self):
        return f"{self.customer.customer_name} - Sale #{self.sale.id}"


# ==================== INVENTORY LOGS ====================

class InventoryLog(models.Model):
    """Inventory audit log"""
    
    ACTION_CHOICES = [
        ('add', 'Add'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('sale', 'Sale'),
        ('restock', 'Restock'),
        ('adjustment', 'Adjustment'),
    ]
    
    barcode = models.ForeignKey(Product, on_delete=models.CASCADE, db_column='barcode')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    quantity_changed = models.IntegerField(null=True, blank=True)
    previous_stock = models.IntegerField(null=True, blank=True)
    new_stock = models.IntegerField(null=True, blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'inventory_logs'
        verbose_name = 'Inventory Log'
        verbose_name_plural = 'Inventory Logs'
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.action} - {self.barcode.product_name}"


# ==================== EXPENSES ====================

class Expense(models.Model):
    """Business expense tracking"""
    EXPENSE_TYPES = [
        ('product_cost', 'Product Cost'),
        ('employee_salary', 'Employee Salary'),  # NEW
        ('rent', 'Rent'),
        ('utilities', 'Utilities'),
        ('marketing', 'Marketing'),
        ('maintenance', 'Maintenance'),
        ('other', 'Other'),
    ]
    expense_type = models.CharField(max_length=50, choices=EXPENSE_TYPES)
    description = models.TextField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    expense_date = models.DateField()
    recorded_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # NEW FIELDS for Feature 2: Link to product if product cost
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    
    # NEW FIELDS for Feature 8: Link to employee if salary expense
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='salary_expenses'
    )
    
    class Meta:
        db_table = 'expenses'
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
        ordering = ['-expense_date']
    
    def __str__(self):
        return f"{self.expense_type} - ${self.amount}"


# ==================== ALERTS ====================

class Alert(models.Model):
    """System alerts and notifications"""
    
    ALERT_TYPES = [
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('system', 'System'),
    ]
    
    SEVERITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    barcode = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True, db_column='barcode')
    severity = models.CharField(max_length=10, choices=SEVERITY_LEVELS, default='medium')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'alerts'
        verbose_name = 'Alert'
        verbose_name_plural = 'Alerts'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.alert_type} - {self.message[:50]}"
