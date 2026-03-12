"""
Custom Permissions for Inventory Management System
All 12 Features - Role-Based Access Control
"""

from rest_framework import permissions


# ==================== ADMIN PERMISSIONS ====================

class IsAdminUser(permissions.BasePermission):
    """
    Permission for admin users only
    Used for: Employee management, expenses, monthly salaries
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )
    
    message = "Admin access required."


# ==================== WORKER/EMPLOYEE PERMISSIONS ====================

class IsWorkerOrAdmin(permissions.BasePermission):
    """
    Permission for workers/employees and admins
    Used for: Creating products, processing sales
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['admin', 'employee']  # Changed 'worker' to 'employee'
        )
    
    message = "Employee or admin access required."


class CanViewEmployees(permissions.BasePermission):
    """
    Permission for employees and admins to view employee list
    Used for: Employee listing/viewing
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['admin', 'employee']
        )
    
    message = "Employee or admin access required to view employee list."


# ==================== FEATURE 1: EMPLOYEE ACCESS ====================

class CanViewSalesData(permissions.BasePermission):
    """
    Feature 1: Employees and admins can view sales data
    Customers cannot view sales data
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['admin', 'employee']
        )
    
    message = "Only admin and employees can view sales data."


class CanViewCustomers(permissions.BasePermission):
    """
    Feature 1: Employees and admins can view customer details
    Customers cannot view other customers
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['admin', 'employee']
        )
    
    message = "Only admin and employees can view customer details."


# ==================== CUSTOMER PERMISSIONS ====================

class IsCustomer(permissions.BasePermission):
    """
    Permission for customers only
    Used for: Customer purchases
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'customer'
        )
    
    message = "Customer access required."


class IsCustomerReadOnly(permissions.BasePermission):
    """
    Customers can only use GET requests (read-only)
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.role == 'customer':
            return request.method in permissions.SAFE_METHODS  # GET, HEAD, OPTIONS
        
        return True
    
    message = "Customers have read-only access."


# ==================== PRODUCT PERMISSIONS ====================

class CanViewProducts(permissions.BasePermission):
    """
    All authenticated users can view products
    Used for: Product listing
    """
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated
    
    message = "Authentication required to view products."


class CanManageProducts(permissions.BasePermission):
    """
    Only workers/employees and admins can manage products
    Customers cannot create/edit/delete products
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role in ['admin', 'employee']
        )
    
    message = "Employee or admin access required to manage products."


# ==================== FEATURE 8: SALARY PERMISSIONS ====================

class CanViewSalaries(permissions.BasePermission):
    """
    Feature 8: Only admin can view employee salaries
    Employees cannot see their own or others' salaries
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )
    
    message = "Only admin can view employee salaries."


# ==================== EXPENSE PERMISSIONS ====================

class CanManageExpenses(permissions.BasePermission):
    """
    Feature 2: Only admin can add and manage expenses
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )
    
    message = "Only admin can manage expenses."