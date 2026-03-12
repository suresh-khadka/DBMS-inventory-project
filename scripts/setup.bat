@echo off
echo ================================================================
echo  COMPLETE INSTALLATION - Django Inventory Management System
echo ================================================================
echo.

cd backend

echo [1/10] Creating virtual environment...
python -m venv venv
echo.

echo [2/10] Activating virtual environment...
call venv\Scripts\activate
echo.

echo [3/10] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo.

echo [4/10] Installing dependencies...
pip install -r requirements.txt --quiet
echo.

echo [5/10] Creating .env file...
if not exist .env (
    copy .env.example .env
    echo .env created. Please edit it with your database password.
) else (
    echo .env already exists.
)
echo.

echo [6/10] Waiting for database creation...
echo Please run these MySQL commands:
echo    mysql -u root -p
echo    CREATE DATABASE inventory_db;
echo    EXIT;
echo.
pause

echo [7/10] Running migrations...
python manage.py makemigrations inventory
python manage.py migrate
echo.

echo [8/10] Creating sample data...
python manage.py create_sample_data
echo.

echo [9/10] Collecting static files...
python manage.py collectstatic --noinput
echo.

echo [10/10] Setup complete!
echo.
echo ================================================================
echo  INSTALLATION SUCCESSFUL!
echo ================================================================
echo.
echo Start server with: python manage.py runserver
echo Access at: http://localhost:8000
echo.
echo Default login:
echo   Admin: admin / admin123
echo.
pause
