#!/bin/bash

# Quick Setup Script for CBT Django Application
# Run this script to set up the application for the first time

echo ""
echo "==================================================="
echo "CBT Examination System - Setup Script"
echo "==================================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "[1/5] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

echo "[2/5] Activating virtual environment..."
source venv/bin/activate

echo "[3/5] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo "[4/5] Running migrations..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "Error: Failed to run migrations"
    exit 1
fi

echo "[5/5] Creating superuser account..."
echo "Please create an admin account:"
python manage.py createsuperuser

echo ""
echo "==================================================="
echo "Setup Complete!"
echo "==================================================="
echo ""
echo "To start the development server, run:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Then visit:"
echo "  - http://localhost:8000/          (Student exam)"
echo "  - http://localhost:8000/admin/    (Admin panel)"
echo ""
