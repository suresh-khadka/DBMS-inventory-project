"""
Management command to create sample data
Usage: python manage.py create_sample_data
"""

from django.core.management.base import BaseCommand
from inventory.models import User, Employee, Customer, Product
from datetime import date
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create sample data for testing'
    
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))
        
        # Create users
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={'role': 'admin', 'is_staff': True, 'is_superuser': True}
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('✓ Admin user created (admin/admin123)'))
        
        worker_user, created = User.objects.get_or_create(
            username='worker1',
            defaults={'role': 'worker'}
        )
        if created:
            worker_user.set_password('worker123')
            worker_user.save()
            self.stdout.write(self.style.SUCCESS('✓ Worker user created (worker1/worker123)'))
        
        customer_user, created = User.objects.get_or_create(
            username='customer1',
            defaults={'role': 'customer'}
        )
        if created:
            customer_user.set_password('customer123')
            customer_user.save()
            self.stdout.write(self.style.SUCCESS('✓ Customer user created (customer1/customer123)'))
        
        # Create employees
        Employee.objects.get_or_create(
            email='admin@inventory.com',
            defaults={
                'employee_name': 'Admin User',
                'role': 'admin',
                'salary': Decimal('5000.00'),
                'hire_date': date.today(),
                'user': admin_user
            }
        )
        
        Employee.objects.get_or_create(
            email='worker1@inventory.com',
            defaults={
                'employee_name': 'Worker One',
                'role': 'worker',
                'salary': Decimal('3000.00'),
                'hire_date': date.today(),
                'user': worker_user
            }
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Employees created'))
        
        # Create customers
        Customer.objects.get_or_create(
            email='customer1@example.com',
            defaults={
                'customer_name': 'John Doe',
                'phone': '1234567890',
                'address': '123 Main St',
                'user': customer_user
            }
        )
        
        self.stdout.write(self.style.SUCCESS('✓ Customers created'))
        
        # Create sample products (barcodes will be auto-generated!)
        products = [
            {
                'product_name': 'Wireless Mouse',
                'description': 'Ergonomic wireless mouse with USB receiver',
                'cost_price': Decimal('15.00'),
                'selling_price': Decimal('25.00'),
                'stock_level': 50,
                'min_stock_level': 10,
                'category': 'Electronics',
                'supplier': 'TechCorp'
            },
            {
                'product_name': 'Laptop Dell XPS 15',
                'description': 'High performance laptop',
                'cost_price': Decimal('1200.00'),
                'selling_price': Decimal('1500.00'),
                'stock_level': 15,
                'min_stock_level': 5,
                'category': 'Computers',
                'supplier': 'Dell Inc'
            },
            {
                'product_name': 'USB-C Cable 2m',
                'description': 'Fast charging USB-C cable',
                'cost_price': Decimal('8.00'),
                'selling_price': Decimal('15.00'),
                'stock_level': 100,
                'min_stock_level': 20,
                'category': 'Accessories',
                'supplier': 'CableCo'
            },
        ]
        
        for product_data in products:
            product, created = Product.objects.get_or_create(
                product_name=product_data['product_name'],
                defaults=product_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Product created: {product.product_name} (Barcode: {product.barcode})'
                    )
                )
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sample data created successfully!'))
        self.stdout.write(self.style.WARNING('\nYou can now login with:'))
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Worker: worker1 / worker123')
        self.stdout.write('  Customer: customer1 / customer123')
