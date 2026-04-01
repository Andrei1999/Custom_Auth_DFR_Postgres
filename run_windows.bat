@echo off
setlocal
cd /d "%~dp0"

if not exist .venv (
    echo [1/4] Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment.
    exit /b 1
)

echo [2/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 exit /b 1

if "%POSTGRES_HOST%"=="" set POSTGRES_HOST=localhost
if "%POSTGRES_PORT%"=="" set POSTGRES_PORT=5432
if "%POSTGRES_DB%"=="" set POSTGRES_DB=custom_auth_db
if "%POSTGRES_USER%"=="" set POSTGRES_USER=postgres
if "%POSTGRES_PASSWORD%"=="" set POSTGRES_PASSWORD=postgres

echo [3/4] Applying migrations...
python manage.py migrate
if errorlevel 1 exit /b 1

echo [4/4] Seeding demo data...
python manage.py seed_demo_data
if errorlevel 1 exit /b 1

echo Starting server at http://127.0.0.1:8000/
python manage.py runserver 127.0.0.1:8000
