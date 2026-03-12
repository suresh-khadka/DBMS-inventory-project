#!/bin/bash
echo "Starting Django Inventory Management System..."
cd backend
source venv/bin/activate
python manage.py runserver
