"""
Serializers for Inventory Management System
Complete API serialization
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import (
    User, Employee, Customer, Product, Sale,
    PurchaseHistory, InventoryLog, Expense, Alert
)

# ==================== USER SERIALIZERS ====================

class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'is_active', 'created_at', 'last_login_date']
        read_only_fields = ['id', 'created_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """User creation serializer with password"""
    
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['username', 'password', 'role']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            role=validated_data.get('role', 'customer')
        )
        return user


# ==================== EMPLOYEE SERIALIZERS ====================

# ==================== UPDATE EXISTING EMPLOYEE SERIALIZER ====================

class EmployeeSerializer(serializers.ModelSerializer):
    """
    Employee serializer with conditional salary display
    Feature 8: Only admin can see salary
    """
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_name', 'email', 'phone',
            'hire_date', 'is_active',
            'user', 'user_username', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Get request from context
        request = self.context.get('request')
        
        # Feature 8: Only admin sees salary
        if request and hasattr(request, 'user') and request.user.role == 'admin':
            self.fields['salary'] = serializers.DecimalField(
                max_digits=10,
                decimal_places=2,
                read_only=True
            )
            self.fields['last_salary_added_date'] = serializers.DateField(
                read_only=True,
                allow_null=True
            )


# ==================== CUSTOMER SERIALIZERS ====================

class CustomerSerializer(serializers.ModelSerializer):
    """
    Enhanced Customer serializer
    Feature 11: Track purchases
    """
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    # NEW: Purchase statistics
    total_purchases_display = serializers.SerializerMethodField()
    total_spent_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Customer
        fields = [
            'id', 'customer_name', 'email', 'phone', 'address',
            'user', 'user_username',
            
            # NEW: Purchase tracking
            'total_purchases', 'total_spent',
            'total_purchases_display', 'total_spent_display',
            
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_purchases', 'total_spent',
            'created_at', 'updated_at'
        ]
    
    def get_total_purchases_display(self, obj):
        """Format total purchases"""
        return f"{obj.total_purchases} purchase(s)"
    
    def get_total_spent_display(self, obj):
        """Format total spent with rupee symbol"""
        return f"₹{obj.total_spent:,.2f}"


# ==================== PRODUCT SERIALIZERS ====================

class ProductSerializer(serializers.ModelSerializer):
    """
    Enhanced Product serializer
    Feature 12: Discount pricing
    Feature 6: Top products tracking
    """
    
    barcode = serializers.CharField(read_only=True)
    profit_margin = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    
    # NEW: Feature 12 - Discount fields
    final_price = serializers.SerializerMethodField()
    has_discount = serializers.SerializerMethodField()
    savings = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'barcode', 'product_name', 'description',
            'cost_price', 'selling_price',
            
            # NEW: Discount fields
            'discount_price', 'discount_percentage',
            'final_price', 'has_discount', 'savings',
            
            'stock_level', 'min_stock_level',
            'category', 'supplier', 'is_active',
            'profit_margin', 'stock_status',
            
            # NEW: Sales tracking
            'total_sales_count', 'total_revenue',
            
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'barcode', 'discount_percentage',
            'total_sales_count', 'total_revenue',
            'created_at', 'updated_at'
        ]
    
    def get_profit_margin(self, obj):
        """Calculate profit margin percentage"""
        if obj.cost_price > 0:
            # Use final price (after discount) for margin calculation
            final_price = obj.get_final_price()
            margin = ((final_price - obj.cost_price) / obj.cost_price) * 100
            return round(margin, 2)
        return 0
    
    def get_stock_status(self, obj):
        """Get stock status"""
        if obj.stock_level == 0:
            return 'out_of_stock'
        elif obj.stock_level <= obj.min_stock_level:
            return 'low_stock'
        else:
            return 'in_stock'
    
    # NEW: Feature 12 methods
    def get_final_price(self, obj):
        """Get final price after discount"""
        return obj.get_final_price()
    
    def get_has_discount(self, obj):
        """Check if product has active discount"""
        return obj.discount_price is not None and obj.discount_price < obj.selling_price
    
    def get_savings(self, obj):
        """Calculate savings amount if discount applied"""
        if self.get_has_discount(obj):
            return obj.selling_price - obj.discount_price
        return 0
    
    def validate(self, data):
        """Validate product data"""
        # Validate selling price >= cost price
        if 'selling_price' in data and 'cost_price' in data:
            if data['selling_price'] < data['cost_price']:
                raise serializers.ValidationError(
                    "Selling price must be greater than or equal to cost price"
                )
        
        # NEW: Validate discount price
        if 'discount_price' in data and data.get('discount_price'):
            selling_price = data.get('selling_price') or (
                self.instance.selling_price if self.instance else None
            )
            if selling_price and data['discount_price'] >= selling_price:
                raise serializers.ValidationError(
                    "Discount price must be less than selling price"
                )
        
        return data


# ==================== SALE SERIALIZERS ====================

# ==================== UPDATE EXISTING SALE SERIALIZER ====================

class SaleSerializer(serializers.ModelSerializer):
    """
    Enhanced Sale serializer
    Feature 12: Track discount application
    Feature 11: Customer purchases
    """
    
    product_name = serializers.CharField(source='barcode.product_name', read_only=True)
    customer_name = serializers.CharField(source='customer.customer_name', read_only=True)
    employee_name = serializers.CharField(source='processed_by.employee_name', read_only=True)
    
    # NEW: Display fields
    total_display = serializers.SerializerMethodField()
    discount_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Sale
        fields = [
            'id', 'barcode', 'product_name',
            'customer', 'customer_name',
            'quantity_sold', 'unit_price', 'total_amount',
            'sale_date', 'processed_by', 'employee_name',
            'payment_method',
            
            # NEW: Discount tracking
            'discount_applied', 'discount_amount',
            'total_display', 'discount_display'
        ]
        read_only_fields = [
            'id', 'sale_date', 'total_amount',
            'discount_applied', 'discount_amount'
        ]
    
    def get_total_display(self, obj):
        """Format total with rupee symbol"""
        return f"₹{obj.total_amount:,.2f}"
    
    def get_discount_display(self, obj):
        """Format discount if applied"""
        if obj.discount_applied:
            return f"₹{obj.discount_amount:,.2f} saved"
        return "No discount"
    
    def validate(self, data):
        """Validate sale data"""
        product = data.get('barcode')
        quantity = data.get('quantity_sold')
        
        # Check stock availability
        if product and quantity:
            if product.stock_level < quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock! Available: {product.stock_level}, Requested: {quantity}"
                )
        
        # Set unit price from product if not provided
        if product and not data.get('unit_price'):
            # Use final price (with discount if available)
            data['unit_price'] = product.get_final_price()
        
        return data


class SaleDetailSerializer(SaleSerializer):
    """Detailed sale serializer with product info"""
    
    product = ProductSerializer(source='barcode', read_only=True)
    customer_details = CustomerSerializer(source='customer', read_only=True)
    
    class Meta(SaleSerializer.Meta):
        fields = SaleSerializer.Meta.fields + ['product', 'customer_details']


# ==================== INVENTORY LOG SERIALIZERS ====================

class InventoryLogSerializer(serializers.ModelSerializer):
    """Inventory log serializer"""
    
    product_name = serializers.CharField(source='barcode.product_name', read_only=True)
    performed_by_username = serializers.CharField(source='performed_by.username', read_only=True)
    
    class Meta:
        model = InventoryLog
        fields = [
            'id', 'barcode', 'product_name',
            'action', 'quantity_changed',
            'previous_stock', 'new_stock',
            'performed_by', 'performed_by_username',
            'timestamp', 'notes'
        ]
        read_only_fields = ['id', 'timestamp']


# ==================== EXPENSE SERIALIZERS ====================

class ExpenseSerializer(serializers.ModelSerializer):
    """
    Enhanced Expense serializer
    Feature 2: Track all expense types
    Feature 8: Employee salary expenses
    """
    
    recorded_by_name = serializers.CharField(
        source='recorded_by.employee_name',
        read_only=True
    )
    employee_name = serializers.CharField(
        source='employee.employee_name',
        read_only=True
    )
    product_name = serializers.CharField(
        source='product.product_name',
        read_only=True
    )
    
    # NEW: Display field
    amount_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Expense
        fields = [
            'id', 'expense_type', 'description', 'amount',
            'expense_date',
            'recorded_by', 'recorded_by_name',
            
            # NEW: Links to product/employee
            'product', 'product_name',
            'employee', 'employee_name',
            
            'amount_display',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_amount_display(self, obj):
        """Format amount with rupee symbol"""
        return f"₹{obj.amount:,.2f}"


# ==================== ALERT SERIALIZERS ====================

class AlertSerializer(serializers.ModelSerializer):
    """Alert serializer for low stock and top products"""
    
    product_name = serializers.CharField(source='barcode.product_name', read_only=True)
    product_stock = serializers.IntegerField(source='barcode.stock_level', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'alert_type', 'message',
            'barcode', 'product_name', 'product_stock',
            'severity', 'is_read', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# ==================== PURCHASE HISTORY SERIALIZERS ====================

class PurchaseHistorySerializer(serializers.ModelSerializer):
    """Purchase history serializer"""
    
    customer_name = serializers.CharField(source='customer.customer_name', read_only=True)
    sale_details = SaleSerializer(source='sale', read_only=True)
    
    class Meta:
        model = PurchaseHistory
        fields = [
            'id', 'customer', 'customer_name',
            'sale', 'sale_details', 'purchase_date'
        ]
        read_only_fields = ['id', 'purchase_date']


# ==================== CUSTOMER REGISTRATION (Feature 4) ====================

class CustomerRegistrationSerializer(serializers.Serializer):
    """
    Serializer for customer self-registration
    Feature 4: Customer sign-up
    Feature 5: Unique username validation
    """
    
    # User fields
    username = serializers.CharField(
        required=True,
        min_length=3,
        max_length=50,
        help_text="Unique username for login"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=6,
        style={'input_type': 'password'},
        help_text="Password (minimum 6 characters)"
    )
    
    # Customer fields
    customer_name = serializers.CharField(
        required=True,
        max_length=100,
        help_text="Full name"
    )
    email = serializers.EmailField(
        required=True,
        help_text="Email address"
    )
    phone = serializers.CharField(
        required=False,
        max_length=20,
        allow_blank=True,
        help_text="Phone number (optional)"
    )
    address = serializers.CharField(
        required=False,
        allow_blank=True,
        style={'base_template': 'textarea.html'},
        help_text="Full address (optional)"
    )
    
    def validate_username(self, value):
        """
        Feature 5: Check username uniqueness across all users
        Case-insensitive check
        """
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "This username is already taken. Please choose another."
            )
        return value
    
    def validate_email(self, value):
        """Check email uniqueness"""
        if Customer.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "This email is already registered."
            )
        return value
    
    def validate_password(self, value):
        """Validate password strength"""
        if len(value) < 6:
            raise serializers.ValidationError(
                "Password must be at least 6 characters long."
            )
        return value
    
    def create(self, validated_data):
        """
        Create both User and Customer records
        """
        # Extract user data
        username = validated_data['username']
        password = validated_data['password']
        email = validated_data['email']
        customer_name = validated_data['customer_name']
        
        # Create User first
        user = User.objects.create_user(
            username=username,
            password=password,
            role='customer',
            email=email,
            full_name=customer_name,
            phone=validated_data.get('phone', '')
        )
        
        # Create Customer profile
        customer = Customer.objects.create(
            user=user,
            customer_name=customer_name,
            email=email,
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', '')
        )
        
        return customer
    
    def to_representation(self, instance):
        """Return customer data (without password)"""
        return {
            'id': instance.id,
            'username': instance.user.username,
            'customer_name': instance.customer_name,
            'email': instance.email,
            'phone': instance.phone
        }


# ==================== EMPLOYEE MANAGEMENT (Feature 3) ====================

class EmployeeCreateSerializer(serializers.Serializer):
    """
    Serializer for admin to create employees
    Feature 3: Employee with username, password, salary
    Feature 5: Unique username validation
    """
    
    # User fields
    username = serializers.CharField(
        required=True,
        min_length=3,
        max_length=50,
        write_only=True
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=6,
        style={'input_type': 'password'}
    )
    
    # Employee fields
    employee_name = serializers.CharField(required=True, max_length=100)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=False, max_length=20, allow_blank=True)
    salary = serializers.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=2,
        min_value=0,
        help_text="Monthly salary in ₹"
    )
    hire_date = serializers.DateField(required=True)
    
    def validate_username(self, value):
        """Feature 5: Check username uniqueness"""
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "This username already exists. Please choose another."
            )
        return value
    
    def validate_email(self, value):
        """Check email uniqueness"""
        if Employee.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "This email is already registered for another employee."
            )
        return value
    
    def create(self, validated_data):
        """Create User and Employee"""
        # Extract user data
        username = validated_data.pop('username')
        password = validated_data.pop('password')
        
        # Create User
        user = User.objects.create_user(
            username=username,
            password=password,
            role='employee'
        )
        
        # Create Employee
        employee = Employee.objects.create(
            user=user,
            **validated_data
        )
        
        return employee
    

# ==================== REPORT SERIALIZERS (Feature 7) ====================

class ProfitLossReportSerializer(serializers.Serializer):
    """
    Serializer for profit/loss reports
    Feature 7: Daily/Weekly/Monthly reports
    """
    
    period = serializers.CharField(read_only=True)
    start_date = serializers.DateField(read_only=True)
    end_date = serializers.DateField(read_only=True)
    revenue = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    expenses = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    profit = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    profit_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    currency = serializers.CharField(default='₹', read_only=True)
    status = serializers.SerializerMethodField()
    
    def get_status(self, obj):
        """Return profit or loss status"""
        return 'profit' if obj.get('profit', 0) >= 0 else 'loss'


class DashboardStatsSerializer(serializers.Serializer):
    """
    Serializer for enhanced dashboard
    Feature 10: Dashboard with ₹ and today's sales
    """
    
    currency = serializers.CharField(default='₹', read_only=True)
    
    # Today's sales
    today_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    today_sales_count = serializers.IntegerField()
    
    # Overall stats
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_revenue = serializers.DecimalField(max_digits=12, decimal_places=2)
    profit_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    profit_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Product stats
    total_products = serializers.IntegerField()
    low_stock_count = serializers.IntegerField()