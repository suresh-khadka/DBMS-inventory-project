@echo off
echo ================================================================
echo  DJANGO INVENTORY SYSTEM - QUICK SETUP
echo  Auto-Generated Barcodes System
echo ================================================================
echo.

echo [1/8] Creating virtual environment...
python -m venv venv
echo.

echo [2/8] Activating virtual environment...
call venv\Scripts\activate
echo.

echo [3/8] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo.

echo [4/8] Installing Django packages...
pip install Django==4.2.7 djangorestframework==3.14.0 django-cors-headers==4.3.1 PyMySQL==1.1.0 python-dotenv==1.0.0 bcrypt==4.1.2 PyJWT==2.8.0 --quiet
echo.

echo [5/8] Creating .env file...
if not exist .env (
    copy .env.example .env
    echo .env file created. Please edit it with your database password.
) else (
    echo .env already exists.
)
echo.

echo [6/8] Creating database...
echo Please create the database manually:
echo    mysql -u root -p
echo    CREATE DATABASE inventory_db;
echo    EXIT;
echo.
pause

echo [7/8] Running migrations...
python manage.py makemigrations inventory
python manage.py migrate
echo.

echo [8/8] Creating sample data...
python manage.py create_sample_data
echo.

echo ================================================================
echo  SETUP COMPLETE!
echo ================================================================
echo.
echo You can now start the server:
echo    python manage.py runserver
echo.
echo Then open: http://localhost:8000
echo.
echo Login credentials:
echo    Admin: admin / admin123
echo    Worker: worker1 / worker123
echo    Customer: customer1 / customer123
echo.
echo ================================================================
pause
