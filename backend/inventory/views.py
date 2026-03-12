"""
API Views for Inventory Management System
Complete REST API with all endpoints
"""

from django.shortcuts import get_object_or_404
from django.db.models import Sum, Count, F, Q
from django.utils import timezone
from datetime import timedelta, date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import jwt
from django.conf import settings
from decimal import Decimal

from .models import (
    User, Employee, Customer, Product, Sale,
    InventoryLog, Expense, Alert, PurchaseHistory
)
from .serializers import (
    UserSerializer, EmployeeSerializer, CustomerSerializer,
    ProductSerializer, SaleSerializer, SaleDetailSerializer,
    InventoryLogSerializer, ExpenseSerializer, AlertSerializer,
    PurchaseHistorySerializer
)
from .permissions import (
    IsAdminUser,
    IsWorkerOrAdmin,
    CanViewSalesData,
    CanViewCustomers,
    CanViewProducts,
    CanManageProducts,
    CanViewSalaries,
    CanManageExpenses,
    IsCustomer,
    IsCustomerReadOnly
)


# ==================== AUTHENTICATION ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """User login - returns JWT token"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'success': False, 'error': 'Username and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(username=username)
        if user.check_password(password):
            # Create JWT token
            payload = {
                'user_id': user.id,
                'username': user.username,
                'role': user.role,
                'exp': timezone.now() + timedelta(hours=24)
            }
            token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            
            # Update last login
            user.last_login_date = timezone.now()
            user.save()
            
            return Response({
                'success': True,
                'token': token,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'role': user.role
                }
            })
        else:
            return Response(
                {'success': False, 'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    except User.DoesNotExist:
        return Response(
            {'success': False, 'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['POST'])
def logout_view(request):
    """User logout"""
    return Response({'success': True, 'message': 'Logged out successfully'})


@api_view(['GET'])
def current_user(request):
    """Get current user info"""
    # Simple version - in production use proper JWT verification
    return Response({'success': True, 'user': UserSerializer(request.user).data})


# ==================== DASHBOARD ====================

@api_view(['GET'])
@permission_classes([IsWorkerOrAdmin])
def dashboard_stats(request):
    """Get dashboard statistics"""
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    # Product stats
    total_products = Product.objects.filter(is_active=True).count()
    low_stock = Product.objects.filter(
        stock_level__lte=F('min_stock_level'),
        is_active=True
    ).count()
    
    # Sales stats
    today_sales = Sale.objects.filter(sale_date__date=today)
    today_revenue = today_sales.aggregate(total=Sum('total_amount'))['total'] or 0
    today_count = today_sales.count()
    
    month_sales = Sale.objects.filter(sale_date__date__gte=month_start)
    month_revenue = month_sales.aggregate(total=Sum('total_amount'))['total'] or 0
    month_count = month_sales.count()
    
    # Employee and customer counts
    employees = Employee.objects.filter(is_active=True).count()
    customers = Customer.objects.count()
    
    # Unread alerts
    unread_alerts = Alert.objects.filter(is_read=False).count()
    
    return Response({
        'success': True,
        'data': {
            'products': {
                'total': total_products,
                'lowStock': low_stock
            },
            'sales': {
                'today': {
                    'totalSales': today_count,
                    'totalRevenue': float(today_revenue)
                },
                'thisMonth': {
                    'totalSales': month_count,
                    'totalRevenue': float(month_revenue)
                }
            },
            'employees': employees,
            'customers': customers,
            'unreadAlerts': unread_alerts
        }
    })


# ==================== PRODUCTS ====================

@api_view(['GET'])
@permission_classes([CanViewProducts])
def product_list(request):
    """List all active products"""
    products = Product.objects.filter(is_active=True).order_by('-created_at')
    serializer = ProductSerializer(products, many=True)
    return Response({'success': True, 'data': serializer.data})


# ==================== FEATURE 12: PRODUCT WITH DISCOUNT ====================

# FIND your existing product_create view and UPDATE it:

@api_view(['POST'])
@permission_classes([CanManageProducts])
def product_create(request):
    """
    Create product with optional discount
    POST /api/products/create/
    
    Body:
    {
        "product_name": "Wireless Mouse",
        "description": "Ergonomic mouse",
        "cost_price": "500",
        "selling_price": "800",
        "discount_price": "650",  // OPTIONAL
        "stock_level": 50,
        "min_stock_level": 10,
        "category": "Electronics",
        "supplier": "TechCorp"
    }
    """
    data = request.data.copy()
    
    # Validate discount price
    if 'discount_price' in data and data['discount_price']:
        selling_price = Decimal(data.get('selling_price', 0))
        discount_price = Decimal(data['discount_price'])
        
        if discount_price >= selling_price:
            return Response({
                'success': False,
                'error': 'Discount price must be less than selling price'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    serializer = ProductSerializer(data=data)
    
    if serializer.is_valid():
        product = serializer.save()
        
        # Calculate discount percentage (already done in model.save())
        discount_info = {}
        if product.discount_price:
            discount_info = {
                'has_discount': True,
                'discount_percentage': float(product.discount_percentage),
                'original_price': float(product.selling_price),
                'discount_price': float(product.discount_price),
                'savings': float(product.selling_price - product.discount_price)
            }
        else:
            discount_info = {
                'has_discount': False
            }
        
        # Create inventory log
        InventoryLog.objects.create(
            barcode=product,
            action='add',
            quantity_changed=product.stock_level,
            new_stock=product.stock_level,
            performed_by=request.user,
            notes=f"Product created with barcode: {product.barcode}"
        )
        
        return Response({
            'success': True,
            'message': 'Product created successfully',
            'product': {
                'barcode': product.barcode,
                'product_name': product.product_name,
                'selling_price': float(product.selling_price),
                **discount_info
            },
            'currency': 'Rs'
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([CanViewProducts]) 
def product_detail(request, barcode):
    """Get product by barcode"""
    product = get_object_or_404(Product, barcode=barcode, is_active=True)
    serializer = ProductSerializer(product)
    return Response({'success': True, 'data': serializer.data})


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def product_update(request, barcode):
    """Update product"""
    product = get_object_or_404(Product, barcode=barcode)
    
    old_stock = product.stock_level
    serializer = ProductSerializer(product, data=request.data, partial=True)
    
    if serializer.is_valid():
        product = serializer.save()
        
        # Log stock changes
        if old_stock != product.stock_level:
            InventoryLog.objects.create(
                barcode=product,
                action='update',
                quantity_changed=product.stock_level - old_stock,
                previous_stock=old_stock,
                new_stock=product.stock_level,
                notes="Stock updated"
            )
        
        return Response({
            'success': True,
            'message': 'Product updated successfully'
        })
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def product_delete(request, barcode):
    """Soft delete product"""
    product = get_object_or_404(Product, barcode=barcode)
    product.is_active = False
    product.save()
    
    InventoryLog.objects.create(
        barcode=product,
        action='delete',
        notes="Product deactivated"
    )
    
    return Response({
        'success': True,
        'message': 'Product deleted successfully'
    })


@api_view(['GET'])
@permission_classes([IsWorkerOrAdmin]) 
def low_stock_products(request):
    """Get products with low stock"""
    products = Product.objects.filter(
        stock_level__lte=F('min_stock_level'),
        is_active=True
    ).order_by('stock_level')
    
    serializer = ProductSerializer(products, many=True)
    return Response({'success': True, 'data': serializer.data})


# ==================== SALES ====================

@api_view(['GET'])
@permission_classes([CanViewSalesData])
def sale_list(request):
    """
    List sales - Admin and Employees can view
    GET /api/sales/
    """
    # Employees can view sales data
    if request.user.role not in ['admin', 'employee']:
        return Response({
            'success': False,
            'error': 'Access denied'
        }, status=status.HTTP_403_FORBIDDEN)
    
    limit = int(request.GET.get('limit', 50))
    sales = Sale.objects.all().select_related(
        'barcode', 'customer', 'processed_by'
    ).order_by('-sale_date')[:limit]
    
    serializer = SaleSerializer(sales, many=True)
    return Response({'success': True, 'data': serializer.data})



@api_view(['POST'])
@permission_classes([IsWorkerOrAdmin])
def sale_create(request):
    """Create new sale - auto updates stock"""
    serializer = SaleSerializer(data=request.data)
    
    if serializer.is_valid():
        sale = serializer.save()
        
        # Create purchase history if customer provided
        if sale.customer:
            PurchaseHistory.objects.create(
                customer=sale.customer,
                sale=sale
            )
        
        return Response({
            'success': True,
            'message': 'Sale created successfully',
            'data': {
                'id': sale.id,
                'barcode': sale.barcode.barcode,
                'total_amount': float(sale.total_amount)
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([CanViewSalesData])
def sale_detail(request, pk):
    """Get sale details"""
    sale = get_object_or_404(Sale, pk=pk)
    serializer = SaleDetailSerializer(sale)
    return Response({'success': True, 'data': serializer.data})


# ==================== EMPLOYEES ====================

@api_view(['GET'])
@permission_classes([IsAdminUser])
def employee_list(request):
    """List all active employees"""
    employees = Employee.objects.filter(is_active=True)
    serializer = EmployeeSerializer(employees, many=True, context={'request': request})
    return Response({'success': True, 'data': serializer.data})


@api_view(['POST'])
@permission_classes([IsAdminUser])
def employee_create(request):
    """Create new employee"""
    serializer = EmployeeSerializer(data=request.data)
    if serializer.is_valid():
        employee = serializer.save()
        return Response({
            'success': True,
            'message': 'Employee created successfully',
            'data': {'id': employee.id}
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def employee_detail(request, pk):
    """Get employee details"""
    employee = get_object_or_404(Employee, pk=pk)
    serializer = EmployeeSerializer(employee, context={'request': request})
    return Response({'success': True, 'data': serializer.data})


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def employee_update(request, pk):
    """Update employee"""
    employee = get_object_or_404(Employee, pk=pk)
    serializer = EmployeeSerializer(employee, data=request.data, partial=True, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Employee updated successfully'
        })
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def employee_delete(request, pk):
    """Soft delete employee"""
    employee = get_object_or_404(Employee, pk=pk)
    employee.is_active = False
    employee.save()
    return Response({
        'success': True,
        'message': 'Employee deleted successfully'
    })


# ==================== CUSTOMERS ====================

@api_view(['GET'])
@permission_classes([CanViewCustomers])
def customer_list(request):
    """List all customers"""
    customers = Customer.objects.all()
    serializer = CustomerSerializer(customers, many=True)
    return Response({'success': True, 'data': serializer.data})


@api_view(['POST'])
@permission_classes([IsWorkerOrAdmin]) 
def customer_create(request):
    """Create new customer"""
    serializer = CustomerSerializer(data=request.data)
    if serializer.is_valid():
        customer = serializer.save()
        return Response({
            'success': True,
            'message': 'Customer created successfully',
            'data': {'id': customer.id}
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([CanViewCustomers])  
def customer_detail(request, pk):
    """Get customer details"""
    customer = get_object_or_404(Customer, pk=pk)
    serializer = CustomerSerializer(customer)
    return Response({'success': True, 'data': serializer.data})


@api_view(['PUT'])
@permission_classes([IsWorkerOrAdmin])
def customer_update(request, pk):
    """Update customer"""
    customer = get_object_or_404(Customer, pk=pk)
    serializer = CustomerSerializer(customer, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'success': True,
            'message': 'Customer updated successfully'
        })
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAdminUser]) 
def customer_delete(request, pk):
    """Delete customer"""
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return Response({
        'success': True,
        'message': 'Customer deleted successfully'
    })


@api_view(['GET'])
@permission_classes([CanViewCustomers])
def customer_purchases(request, pk):
    """Get customer purchase history"""
    customer = get_object_or_404(Customer, pk=pk)
    purchases = PurchaseHistory.objects.filter(customer=customer)
    serializer = PurchaseHistorySerializer(purchases, many=True)
    return Response({'success': True, 'data': serializer.data})


# ==================== EXPENSES ====================

@api_view(['GET'])
@permission_classes([IsAdminUser])
def expense_list(request):
    """List all expenses"""
    expenses = Expense.objects.all().order_by('-expense_date')
    serializer = ExpenseSerializer(expenses, many=True)
    return Response({'success': True, 'data': serializer.data})


@api_view(['POST'])
@permission_classes([CanManageExpenses]) 
def expense_create(request):
    """Create new expense"""
    serializer = ExpenseSerializer(data=request.data)
    if serializer.is_valid():
        expense = serializer.save()
        return Response({
            'success': True,
            'message': 'Expense created successfully',
            'data': {'id': expense.id}
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def expense_detail(request, pk):
    """Get, update, or delete expense details"""
    expense = get_object_or_404(Expense, pk=pk)
    
    if request.method == 'GET':
        serializer = ExpenseSerializer(expense)
        return Response({'success': True, 'data': serializer.data})
    
    elif request.method == 'PUT':
        permission_classes = [CanManageExpenses]
        # Check permission
        for perm_class in permission_classes:
            permission = perm_class()
            if not permission.has_permission(request, None):
                return Response({
                    'success': False,
                    'error': 'You do not have permission to update expenses'
                }, status=status.HTTP_403_FORBIDDEN)
        
        expense_type = request.data.get('expense_type', expense.expense_type)
        amount = request.data.get('amount', expense.amount)
        expense_date = request.data.get('expense_date', expense.expense_date)
        description = request.data.get('description', expense.description)
        
        if not all([expense_type, amount, expense_date]):
            return Response({
                'success': False,
                'error': 'Expense type, amount, and date are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            expense.expense_type = expense_type
            expense.amount = Decimal(amount)
            expense.expense_date = expense_date
            expense.description = description
            expense.save()
            
            serializer = ExpenseSerializer(expense)
            return Response({
                'success': True,
                'message': 'Expense updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        permission_classes = [CanManageExpenses]
        # Check permission
        for perm_class in permission_classes:
            permission = perm_class()
            if not permission.has_permission(request, None):
                return Response({
                    'success': False,
                    'error': 'You do not have permission to delete expenses'
                }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            expense.delete()
            return Response({
                'success': True,
                'message': 'Expense deleted successfully'
            }, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


# ==================== REPORTS ====================



@api_view(['GET'])
@permission_classes([IsWorkerOrAdmin])
def inventory_report(request):
    """Get inventory report"""
    products = Product.objects.filter(is_active=True)
    
    total_value = sum(
        float(p.stock_level * p.cost_price)
        for p in products
    )
    
    low_stock_count = products.filter(
        stock_level__lte=F('min_stock_level')
    ).count()
    
    return Response({
        'success': True,
        'data': {
            'totalProducts': products.count(),
            'totalValue': round(total_value, 2),
            'lowStock': low_stock_count
        }
    })


@api_view(['GET'])
@permission_classes([IsWorkerOrAdmin])
def sales_trend(request):
    """Get sales trend for last 7 days"""
    from django.db.models.functions import TruncDate
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    sales = Sale.objects.filter(sale_date__date__gte=week_ago) \
        .annotate(date=TruncDate('sale_date')) \
        .values('date') \
        .annotate(
            total=Sum('total_amount'),
            count=Count('id')
        ) \
        .order_by('date')
    
    return Response({'success': True, 'data': list(sales)})


# ==================== ALERTS ====================

@api_view(['GET'])
@permission_classes([IsWorkerOrAdmin])
def alert_list(request):
    """List all alerts"""
    alerts = Alert.objects.all().order_by('-created_at')
    serializer = AlertSerializer(alerts, many=True)
    return Response({'success': True, 'data': serializer.data})


@api_view(['PUT'])
@permission_classes([IsWorkerOrAdmin]) 
def alert_mark_read(request, pk):
    """Mark alert as read"""
    alert = get_object_or_404(Alert, pk=pk)
    alert.is_read = True
    alert.save()
    return Response({
        'success': True,
        'message': 'Alert marked as read'
    })


# ==================== INVENTORY LOGS ====================

@api_view(['GET'])
@permission_classes([IsWorkerOrAdmin])
def inventory_log_list(request):
    """List inventory logs"""
    logs = InventoryLog.objects.all().order_by('-timestamp')[:100]
    serializer = InventoryLogSerializer(logs, many=True)
    return Response({'success': True, 'data': serializer.data})


# ==================== FEATURE 4: CUSTOMER REGISTRATION ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def customer_register(request):
    """
    Customer sign-up endpoint
    POST /api/auth/customer-register/
    
    Body:
    {
        "username": "customer123",
        "password": "password123",
        "customer_name": "John Doe",
        "email": "john@example.com",
        "phone": "1234567890",
        "address": "123 Main St"
    }
    """
    username = request.data.get('username')
    password = request.data.get('password')
    customer_name = request.data.get('customer_name')
    email = request.data.get('email')
    phone = request.data.get('phone', '')
    address = request.data.get('address', '')
    
    # Validation
    if not username or not password or not customer_name or not email:
        return Response({
            'success': False,
            'error': 'Username, password, name, and email are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Feature 5: Check username uniqueness (case-insensitive)
    if User.objects.filter(username__iexact=username).exists():
        return Response({
            'success': False,
            'error': 'Username already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check email uniqueness
    if Customer.objects.filter(email__iexact=email).exists():
        return Response({
            'success': False,
            'error': 'Email already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Create user account
        user = User.objects.create_user(
            username=username,
            password=password,
            role='customer',
            email=email,
            phone=phone,
            full_name=customer_name
        )
        
        # Create customer profile
        customer = Customer.objects.create(
            user=user,
            customer_name=customer_name,
            email=email,
            phone=phone,
            address=address
        )
        
        return Response({
            'success': True,
            'message': 'Account created successfully! You can now login.',
            'customer_id': customer.id,
            'username': username
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    

# ==================== FEATURE 3: EMPLOYEE MANAGEMENT ====================

@api_view(['POST'])
@permission_classes([IsAdminUser])
def employee_create(request):
    """
    Admin creates new employee with username, password, and salary
    POST /api/employees/create/
    
    Body:
    {
        "username": "emp001",
        "password": "emppass123",
        "employee_name": "Jane Smith",
        "email": "jane@company.com",
        "phone": "9876543210",
        "salary": "50000",
        "hire_date": "2024-01-15"
    }
    """
    username = request.data.get('username')
    password = request.data.get('password')
    employee_name = request.data.get('employee_name')
    email = request.data.get('email')
    phone = request.data.get('phone', '')
    salary = request.data.get('salary')
    hire_date = request.data.get('hire_date')
    
    # Validation
    if not all([username, password, employee_name, email, salary, hire_date]):
        return Response({
            'success': False,
            'error': 'All fields are required: username, password, name, email, salary, hire_date'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Feature 5: Check username uniqueness
    if User.objects.filter(username__iexact=username).exists():
        return Response({
            'success': False,
            'error': 'Username already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check email uniqueness
    if Employee.objects.filter(email__iexact=email).exists():
        return Response({
            'success': False,
            'error': 'Email already exists'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Create user account for employee
        user = User.objects.create_user(
            username=username,
            password=password,
            role='employee',
            email=email,
            full_name=employee_name
        )
        
        # Create employee profile
        employee = Employee.objects.create(
            user=user,
            employee_name=employee_name,
            email=email,
            phone=phone,
            salary=Decimal(salary),
            hire_date=hire_date,
            is_active=True
        )
        
        return Response({
            'success': True,
            'message': f'Employee {employee_name} created successfully',
            'employee_id': employee.id,
            'username': username
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def employee_list_with_salaries(request):
    """
    Feature 8: Admin-only view to see employee salaries
    GET /api/employees/salaries/
    """
    employees = Employee.objects.filter(is_active=True)
    
    data = []
    for emp in employees:
        data.append({
            'id': emp.id,
            'employee_name': emp.employee_name,
            'email': emp.email,
            'phone': emp.phone,
            'salary': float(emp.salary),
            'hire_date': emp.hire_date,
            'last_salary_added': emp.last_salary_added_date,
            'username': emp.user.username if emp.user else None
        })
    
    return Response({
        'success': True,
        'count': len(data),
        'employees': data,
        'total_monthly_salary': sum(float(e.salary) for e in employees),
        'currency': 'Rs'
    })


# ==================== FEATURE 6: ALERTS & TOP PRODUCTS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_low_stock_alerts(request):
    """
    Get low stock and out of stock products with details
    GET /api/alerts/low-stock/
    """
    # Get low stock products
    low_stock = Product.objects.filter(
        stock_level__lte=F('min_stock_level'),
        stock_level__gt=0,
        is_active=True
    ).order_by('stock_level')
    
    # Get out of stock products
    out_of_stock = Product.objects.filter(
        stock_level=0,
        is_active=True
    )
    
    low_stock_data = []
    for product in low_stock:
        low_stock_data.append({
            'barcode': product.barcode,
            'product_name': product.product_name,
            'stock_level': product.stock_level,
            'min_stock_level': product.min_stock_level,
            'category': product.category,
            'status': 'low_stock',
            'severity': 'medium'
        })
    
    out_of_stock_data = []
    for product in out_of_stock:
        out_of_stock_data.append({
            'barcode': product.barcode,
            'product_name': product.product_name,
            'stock_level': 0,
            'category': product.category,
            'status': 'out_of_stock',
            'severity': 'high'
        })
    
    return Response({
        'success': True,
        'low_stock': {
            'count': len(low_stock_data),
            'products': low_stock_data
        },
        'out_of_stock': {
            'count': len(out_of_stock_data),
            'products': out_of_stock_data
        },
        'total_alerts': len(low_stock_data) + len(out_of_stock_data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_top_selling_products(request):
    """
    Get top 2 selling products
    GET /api/products/top-selling/
    """
    top_products = Product.objects.filter(
        is_active=True,
        total_sales_count__gt=0
    ).order_by('-total_sales_count')[:2]
    
    data = []
    for product in top_products:
        data.append({
            'barcode': product.barcode,
            'product_name': product.product_name,
            'total_sales_count': product.total_sales_count,
            'total_revenue': float(product.total_revenue),
            'selling_price': float(product.selling_price),
            'discount_price': float(product.discount_price) if product.discount_price else None,
            'stock_level': product.stock_level,
            'category': product.category
        })
    
    return Response({
        'success': True,
        'top_products': data,
        'currency': 'Rs'
    })

# ==================== FEATURE 7: PROFIT/LOSS REPORTS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profit_loss_report(request):
    """
    Calculate profit/loss for different periods
    GET /api/reports/profit-loss/?period=daily
    
    Query params:
    - period: daily, weekly, monthly (default: daily)
    """
    period = request.GET.get('period', 'daily')
    today = timezone.now().date()
    
    # Determine date range based on period
    if period == 'daily':
        start_date = today
        period_label = 'Today'
    elif period == 'weekly':
        start_date = today - timedelta(days=7)
        period_label = 'Last 7 Days'
    elif period == 'monthly':
        start_date = today.replace(day=1)
        period_label = 'This Month'
    else:
        start_date = today
        period_label = 'Today'
    
    # Calculate revenue from sales
    sales = Sale.objects.filter(sale_date__date__gte=start_date)
    total_revenue = sales.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    sales_count = sales.count()
    
    # Calculate expenses
    expenses = Expense.objects.filter(expense_date__gte=start_date)
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    expense_count = expenses.count()
    
    # Calculate profit/loss
    profit = total_revenue - total_expenses
    profit_percentage = (profit / total_revenue * 100) if total_revenue > 0 else Decimal('0.00')
    
    # Determine status
    if profit > 0:
        status_text = 'Profit'
        status_color = 'green'
    elif profit < 0:
        status_text = 'Loss'
        status_color = 'red'
    else:
        status_text = 'Break Even'
        status_color = 'yellow'
    
    return Response({
        'success': True,
        'period': period,
        'period_label': period_label,
        'date_range': {
            'start': start_date,
            'end': today
        },
        'revenue': {
            'amount': float(total_revenue),
            'sales_count': sales_count
        },
        'expenses': {
            'amount': float(total_expenses),
            'expense_count': expense_count
        },
        'profit_loss': {
            'amount': float(profit),
            'percentage': float(profit_percentage),
            'status': status_text,
            'status_color': status_color
        },
        'currency': 'Rs'
    })

# ==================== FEATURE 8: MONTHLY SALARY EXPENSES ====================

@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_monthly_salaries_to_expenses(request):
    """
    Admin manually adds all employee salaries to expenses
    Should be called on 1st of each month
    POST /api/admin/add-monthly-salaries/
    """
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    
    # Get all active employees
    employees = Employee.objects.filter(is_active=True)
    
    added_count = 0
    skipped_count = 0
    total_amount = Decimal('0.00')
    
    for employee in employees:
        # Check if salary already added this month
        if employee.last_salary_added_date:
            if (employee.last_salary_added_date.month == today.month and 
                employee.last_salary_added_date.year == today.year):
                skipped_count += 1
                continue
        
        # Add salary as expense
        Expense.objects.create(
            expense_type='employee_salary',
            amount=employee.salary,
            expense_date=first_day_of_month,
            employee=employee,
            description=f"Monthly salary for {employee.employee_name} - {today.strftime('%B %Y')}"
        )
        
        # Update last salary added date
        employee.last_salary_added_date = today
        employee.save()
        
        added_count += 1
        total_amount += employee.salary
    
    return Response({
        'success': True,
        'message': f'Added {added_count} employee salaries to expenses',
        'details': {
            'added': added_count,
            'skipped': skipped_count,
            'total_amount': float(total_amount),
            'month': today.strftime('%B %Y')
        },
        'currency': 'Rs'
    })


# ==================== FEATURE 9: BARCODE SCANNING & RECOMMENDATIONS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_product_by_barcode(request, barcode):
    """
    Search product by barcode and get recommendations
    GET /api/products/barcode/<barcode>/
    """
    try:
        product = Product.objects.get(barcode=barcode, is_active=True)
    except Product.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Product not found',
            'barcode': barcode
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Get product data
    product_data = {
        'barcode': product.barcode,
        'product_name': product.product_name,
        'description': product.description,
        'selling_price': float(product.selling_price),
        'discount_price': float(product.discount_price) if product.discount_price else None,
        'final_price': float(product.get_final_price()),
        'has_discount': product.discount_price is not None,
        'discount_percentage': float(product.discount_percentage),
        'stock_level': product.stock_level,
        'category': product.category,
        'supplier': product.supplier
    }
    
    # Get recommended products (same category, excluding current product)
    recommendations = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(barcode=barcode).order_by('-total_sales_count')[:5]
    
    recommendations_data = []
    for rec in recommendations:
        recommendations_data.append({
            'barcode': rec.barcode,
            'product_name': rec.product_name,
            'final_price': float(rec.get_final_price()),
            'stock_level': rec.stock_level,
            'total_sales_count': rec.total_sales_count
        })
    
    return Response({
        'success': True,
        'product': product_data,
        'recommendations': {
            'count': len(recommendations_data),
            'products': recommendations_data
        },
        'currency': 'Rs'
    })

# ==================== FEATURE 10: ENHANCED DASHBOARD (Rs Currency) ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def enhanced_dashboard(request):
    """
    Enhanced dashboard with Indian Rupees and Today's Sales
    GET /api/dashboard/enhanced/
    """
    today = timezone.now().date()
    
    # Today's sales
    today_sales = Sale.objects.filter(sale_date__date=today)
    today_revenue = today_sales.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    today_sales_count = today_sales.count()
    
    # Today's sales products breakdown
    today_products = today_sales.values(
        'barcode__product_name',
        'barcode__barcode'
    ).annotate(
        total_qty=Sum('quantity_sold'),
        total_amount=Sum('total_amount')
    ).order_by('-total_amount')[:10]
    
    # Total expenses (all time)
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    # Total revenue (all time)
    total_revenue = Sale.objects.aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Overall profit/loss
    overall_profit = total_revenue - total_expenses
    profit_percentage = (overall_profit / total_revenue * 100) if total_revenue > 0 else Decimal('0.00')
    
    # Low stock count
    low_stock_count = Product.objects.filter(
        stock_level__lte=F('min_stock_level'),
        is_active=True
    ).count()
    
    # Total products
    total_products = Product.objects.filter(is_active=True).count()
    
    # Total customers
    total_customers = Customer.objects.count()
    
    # Total employees
    total_employees = Employee.objects.filter(is_active=True).count()
    
    return Response({
        'success': True,
        'currency': 'Rs',
        'today_sales': {
            'revenue': float(today_revenue),
            'count': today_sales_count,
            'products': list(today_products)
        },
        'total_expenses': float(total_expenses),
        'total_revenue': float(total_revenue),
        'profit_loss': {
            'amount': float(overall_profit),
            'percentage': float(profit_percentage),
            'status': 'profit' if overall_profit >= 0 else 'loss',
            'color': 'green' if overall_profit >= 0 else 'red'
        },
        'stats': {
            'total_products': total_products,
            'low_stock_count': low_stock_count,
            'total_customers': total_customers,
            'total_employees': total_employees
        }
    })

# ==================== FEATURE 11: CUSTOMER CAN PURCHASE PRODUCTS ====================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def customer_purchase_product(request):
    """
    Allow customers to purchase products
    POST /api/sales/customer-purchase/
    
    Body:
    {
        "barcode": "WIRELESS1234",
        "quantity": 2,
    }
    """
    # Check if user is customer
    if request.user.role != 'customer':
        return Response({
            'success': False,
            'error': 'Only customers can use this endpoint'
        }, status=status.HTTP_403_FORBIDDEN)
    
    barcode = request.data.get('barcode')
    quantity = int(request.data.get('quantity', 1))
    payment_method = request.data.get('payment_method', 'cash')
    
    if not barcode or quantity < 1:
        return Response({
            'success': False,
            'error': 'Barcode and valid quantity required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        product = Product.objects.get(barcode=barcode, is_active=True)
        customer = request.user.customer_profile
    except Product.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Customer.DoesNotExist:
        return Response({
            'success': False,
            'error': 'Customer profile not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check stock availability
    if product.stock_level < quantity:
        return Response({
            'success': False,
            'error': f'Insufficient stock. Only {product.stock_level} available',
            'available_stock': product.stock_level
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Get final price (with discount if available)
    unit_price = product.get_final_price()
    total_amount = unit_price * quantity
    
    # Check if discount applied
    discount_applied = False
    discount_amount = Decimal('0.00')
    if product.discount_price and unit_price == product.discount_price:
        discount_applied = True
        discount_amount = (product.selling_price - product.discount_price) * quantity
    
    try:
        # Create sale
        sale = Sale.objects.create(
            barcode=product,
            customer=customer,
            quantity_sold=quantity,
            unit_price=unit_price,
            total_amount=total_amount,
            payment_method=payment_method,
            discount_applied=discount_applied,
            discount_amount=discount_amount
        )
        
        # Create purchase history
        PurchaseHistory.objects.create(
            customer=customer,
            sale=sale
        )
        
        return Response({
            'success': True,
            'message': 'Purchase successful!',
            'sale': {
                'sale_id': sale.id,
                'product_name': product.product_name,
                'quantity': quantity,
                'unit_price': float(unit_price),
                'total_amount': float(total_amount),
                'discount_applied': discount_applied,
                'discount_saved': float(discount_amount),
                'payment_method': payment_method,
                'sale_date': sale.sale_date
            },
            'product': {
                'remaining_stock': product.stock_level
            },
            'currency': 'Rs'
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    

# ==================== FEATURE 2: EXPENSE TRACKING ====================

@api_view(['POST'])
@permission_classes([CanManageExpenses])
def add_expense(request):
    """
    Admin adds additional expenses (rent, utilities, etc.)
    POST /api/expenses/add/
    
    Body:
    {
        "expense_type": "rent",
        "amount": "25000",
        "expense_date": "2024-03-01",
        "description": "Office rent for March 2024"
    }
    """
    expense_type = request.data.get('expense_type')
    amount = request.data.get('amount')
    expense_date = request.data.get('expense_date')
    description = request.data.get('description', '')
    
    if not all([expense_type, amount, expense_date]):
        return Response({
            'success': False,
            'error': 'Expense type, amount, and date are required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        expense = Expense.objects.create(
            expense_type=expense_type,
            amount=Decimal(amount),
            expense_date=expense_date,
            description=description,
            recorded_by=request.user.employee_profile if hasattr(request.user, 'employee_profile') else None
        )
        
        return Response({
            'success': True,
            'message': 'Expense added successfully',
            'expense': {
                'id': expense.id,
                'expense_type': expense.expense_type,
                'amount': float(expense.amount),
                'expense_date': expense.expense_date,
                'description': expense.description
            },
            'currency': '₹'
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def expense_summary(request):
    """
    Get expense summary by type
    GET /api/expenses/summary/
    """
    # Group expenses by type
    expense_by_type = Expense.objects.values('expense_type').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    total_expenses = Expense.objects.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    
    return Response({
        'success': True,
        'total_expenses': float(total_expenses),
        'breakdown': list(expense_by_type),
        'currency': 'rs'
    })