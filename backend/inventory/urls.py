"""
URL Configuration for Inventory API
All API endpoints including 12 new features
"""

from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    # ==================== AUTHENTICATION ====================
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/me/', views.current_user, name='current_user'),
    path('auth/customer-register/', views.customer_register, name='customer_register'),  # NEW
    
    # ==================== DASHBOARD ====================
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    path('dashboard/enhanced/', views.enhanced_dashboard, name='enhanced_dashboard'),  # NEW
    
    # ==================== PRODUCTS ====================
    path('products/create/', views.product_create, name='product_create'),
    path('products/low-stock/', views.low_stock_products, name='low_stock_products'),
    path('products/top-selling/', views.get_top_selling_products, name='top_selling_products'),  # NEW
    path('products/barcode/<str:barcode>/', views.search_product_by_barcode, name='search_barcode'),  # NEW
    path('products/', views.product_list, name='product_list'),
    path('products/<str:barcode>/', views.product_detail, name='product_detail'),
    path('products/<str:barcode>/update/', views.product_update, name='product_update'),
    path('products/<str:barcode>/delete/', views.product_delete, name='product_delete'),
    
    # ==================== SALES ====================
    path('sales/', views.sale_list, name='sale_list'),
    path('sales/create/', views.sale_create, name='sale_create'),
    path('sales/<int:pk>/', views.sale_detail, name='sale_detail'),
    path('sales/customer-purchase/', views.customer_purchase_product, name='customer_purchase'),  # NEW
    
    # ==================== EMPLOYEES ====================
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),  # NEW
    path('employees/salaries/', views.employee_list_with_salaries, name='employee_salaries'),  # NEW
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/update/', views.employee_update, name='employee_update'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    
    # ==================== CUSTOMERS ====================
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/update/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('customers/<int:pk>/purchases/', views.customer_purchases, name='customer_purchases'),
    
    # ==================== EXPENSES ====================
    path('expenses/', views.expense_list, name='expense_list'),
    path('expenses/add/', views.add_expense, name='add_expense'),  # NEW
    path('expenses/summary/', views.expense_summary, name='expense_summary'),  # NEW
    path('expenses/<int:pk>/', views.expense_detail, name='expense_detail'),
    
    # ==================== REPORTS ====================
    path('reports/profit-loss/', views.profit_loss_report, name='profit_loss_report'),  # NEW
    path('reports/inventory/', views.inventory_report, name='inventory_report'),
    path('reports/sales-trend/', views.sales_trend, name='sales_trend'),
    
    # ==================== ALERTS ====================
    path('alerts/', views.alert_list, name='alert_list'),
    path('alerts/low-stock/', views.get_low_stock_alerts, name='low_stock_alerts'),  # NEW
    path('alerts/<int:pk>/read/', views.alert_mark_read, name='alert_mark_read'),
    
    # ==================== ADMIN ====================
    path('admin/add-monthly-salaries/', views.add_monthly_salaries_to_expenses, name='add_monthly_salaries'),  # NEW
    
    # ==================== INVENTORY LOGS ====================
    path('inventory-logs/', views.inventory_log_list, name='inventory_log_list'),
]