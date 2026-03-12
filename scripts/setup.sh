#!/bin/bash

echo "================================================================"
echo " COMPLETE INSTALLATION - Django Inventory Management System"
echo "================================================================"
echo

cd backend

echo "[1/10] Creating virtual environment..."
python3 -m venv venv
echo

echo "[2/10] Activating virtual environment..."
source venv/bin/activate
echo

echo "[3/10] Upgrading pip..."
pip install --upgrade pip --quiet
echo

echo "[4/10] Installing dependencies..."
pip install -r requirements.txt --quiet
echo

echo "[5/10] Creating .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env created. Please edit it with your database password."
else
    echo ".env already exists."
fi
echo

echo "[6/10] Please create database:"
echo "   mysql -u root -p"
echo "   CREATE DATABASE inventory_db;"
echo "   EXIT;"
echo
read -p "Press enter when database is created..."

echo "[7/10] Running migrations..."
python manage.py makemigrations inventory
python manage.py migrate
echo

echo "[8/10] Creating sample data..."
python manage.py create_sample_data
echo

echo "[9/10] Collecting static files..."
python manage.py collectstatic --noinput
echo

echo "[10/10] Setup complete!"
echo
echo "================================================================"
echo " INSTALLATION SUCCESSFUL!"
echo "================================================================"
echo
echo "Start server with: python manage.py runserver"
echo "Access at: http://localhost:8000"
echo
echo "Default login:"
echo "  Admin: admin / admin123"
echo
