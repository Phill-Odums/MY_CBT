@echo off
REM Quick Setup Script for CBT Django Application
REM Run this script to set up the application for the first time

echo.
echo ===================================================
echo CBT Examination System - Setup Script
echo ===================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/5] Running migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo Error: Failed to run migrations
    pause
    exit /b 1
)

echo [5/5] Creating superuser account...
echo Please create an admin account:
python manage.py createsuperuser

echo.
echo ===================================================
echo Setup Complete!
echo ===================================================
echo.
echo To start the development server, run:
echo   python manage.py runserver
echo.
echo Then visit:
echo   - http://localhost:8000/          (Student exam)
echo   - http://localhost:8000/admin/    (Admin panel)
echo.
pause
