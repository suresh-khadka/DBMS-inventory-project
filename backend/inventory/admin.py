"""
Django Admin Configuration for Inventory Management
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, Employee, Customer, Product, Sale,
    InventoryLog, Expense, Alert, PurchaseHistory
)


# ==================== USER ADMIN ====================

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin"""
    
    list_display = ['username', 'role', 'is_active', 'is_staff', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['username']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login_date', 'created_at')}),
    )
    
    readonly_fields = ['created_at', 'last_login_date']
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )


# ==================== EMPLOYEE ADMIN ====================

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Employee Admin"""
    
    list_display = ['employee_name', 'email', 'role', 'salary', 'hire_date', 'is_active']
    list_filter = ['role', 'is_active', 'hire_date']
    search_fields = ['employee_name', 'email']
    ordering = ['-created_at']
    date_hierarchy = 'hire_date'
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('employee_name', 'email', 'phone')
        }),
        ('Employment Details', {
            'fields': ('role', 'salary', 'hire_date', 'is_active')
        }),
        ('System', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
    )


# ==================== CUSTOMER ADMIN ====================

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    """Customer Admin"""
    
    list_display = ['customer_name', 'email', 'phone', 'created_at']
    search_fields = ['customer_name', 'email', 'phone']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('customer_name', 'email', 'phone', 'address')
        }),
        ('System', {
            'fields': ('user',),
            'classes': ('collapse',)
        }),
    )


# ==================== PRODUCT ADMIN ====================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Product Admin with Barcode Display"""
    
    list_display = [
        'barcode', 'product_name', 
        'selling_price', 'discount_price', 'discount_percentage',  # NEW
        'total_sales_count', 'total_revenue',  # NEW
        'stock_level', 'is_active'
    ]
    list_filter = ['is_active', 'category']
    search_fields = ['barcode', 'product_name', 'category']
    ordering = ['-created_at']
    readonly_fields = ['barcode', 'discount_percentage', 'total_sales_count', 'total_revenue']    
    fieldsets = (
        ('Product Information', {
            'fields': ('barcode', 'product_name', 'description', 'category')
        }),
        ('Pricing', {
            'fields': ('cost_price', 'selling_price')
        }),
        ('Inventory', {
            'fields': ('stock_level', 'min_stock_level')
        }),
        ('Supplier', {
            'fields': ('supplier',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make barcode readonly after creation"""
        if obj:  # Editing existing object
            return self.readonly_fields
        return ['created_at', 'updated_at']  # Creating new object


# ==================== SALE ADMIN ====================

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    """Sale Admin"""
    
    list_display = [
        'id', 'get_product_name', 'barcode',
        'quantity_sold', 'total_amount',
        'sale_date', 'payment_method'
    ]
    list_filter = ['payment_method', 'sale_date']
    search_fields = ['barcode__product_name', 'barcode__barcode']
    ordering = ['-sale_date']
    date_hierarchy = 'sale_date'
    readonly_fields = ['sale_date', 'total_amount']
    
    fieldsets = (
        ('Sale Information', {
            'fields': ('barcode', 'customer', 'quantity_sold', 'unit_price', 'total_amount')
        }),
        ('Payment', {
            'fields': ('payment_method', 'sale_date')
        }),
        ('Processed By', {
            'fields': ('processed_by',)
        }),
    )
    
    def get_product_name(self, obj):
        return obj.barcode.product_name
    get_product_name.short_description = 'Product'


# ==================== INVENTORY LOG ADMIN ====================

@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    """Inventory Log Admin"""
    
    list_display = [
        'id', 'get_product_name', 'action',
        'quantity_changed', 'new_stock',
        'timestamp', 'get_user'
    ]
    list_filter = ['action', 'timestamp']
    search_fields = ['barcode__product_name', 'notes']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
    
    def get_product_name(self, obj):
        return obj.barcode.product_name
    get_product_name.short_description = 'Product'
    
    def get_user(self, obj):
        return obj.performed_by.username if obj.performed_by else 'System'
    get_user.short_description = 'Performed By'


# ==================== EXPENSE ADMIN ====================

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    """Expense Admin"""
    
    list_display = [
        'id', 'expense_type', 'amount',
        'expense_date', 'get_recorded_by'
    ]
    list_filter = ['expense_type', 'expense_date']
    search_fields = ['expense_type', 'description']
    ordering = ['-expense_date']
    date_hierarchy = 'expense_date'
    readonly_fields = ['created_at']
    
    def get_recorded_by(self, obj):
        return obj.recorded_by.employee_name if obj.recorded_by else 'N/A'
    get_recorded_by.short_description = 'Recorded By'


# ==================== ALERT ADMIN ====================

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    """Alert Admin"""
    
    list_display = [
        'id', 'alert_type', 'get_product_name',
        'severity', 'is_read', 'created_at'
    ]
    list_filter = ['alert_type', 'severity', 'is_read', 'created_at']
    search_fields = ['message', 'barcode__product_name']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    
    actions = ['mark_as_read']
    
    def get_product_name(self, obj):
        return obj.barcode.product_name if obj.barcode else 'N/A'
    get_product_name.short_description = 'Product'
    
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} alert(s) marked as read.')
    mark_as_read.short_description = 'Mark selected alerts as read'


# ==================== PURCHASE HISTORY ADMIN ====================

@admin.register(PurchaseHistory)
class PurchaseHistoryAdmin(admin.ModelAdmin):
    """Purchase History Admin"""
    
    list_display = [
        'id', 'get_customer_name',
        'get_sale_id', 'purchase_date'
    ]
    list_filter = ['purchase_date']
    search_fields = ['customer__customer_name']
    ordering = ['-purchase_date']
    date_hierarchy = 'purchase_date'
    readonly_fields = ['purchase_date']
    
    def get_customer_name(self, obj):
        return obj.customer.customer_name
    get_customer_name.short_description = 'Customer'
    
    def get_sale_id(self, obj):
        return f"Sale #{obj.sale.id}"
    get_sale_id.short_description = 'Sale'


# Customize admin site
admin.site.site_header = "Inventory Management System"
admin.site.site_title = "Inventory Admin"
admin.site.index_title = "Welcome to Inventory Management"
