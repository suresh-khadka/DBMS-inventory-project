#!/bin/bash
set -e

echo "🔨 Building Django Inventory System..."

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Collect static files
echo "📊 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "🗄️  Running database migrations..."
python manage.py migrate --noinput

echo "✅ Build complete!"
