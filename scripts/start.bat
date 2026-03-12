@echo off
echo Starting Django Inventory Management System...
cd backend
call venv\Scripts\activate
python manage.py runserver
