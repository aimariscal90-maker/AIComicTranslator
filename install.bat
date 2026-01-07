@echo off
echo ============================================
echo   AI Comic Translator - Installer
echo ============================================

echo [1/4] Checking Python...
python --version
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit /b
)

echo [2/4] Setting up Backend Virtual Environment...
cd backend
if not exist venv (
    echo Creating venv...
    python -m venv venv
)
call venv\Scripts\activate

echo Installing Python dependencies...
pip install -r requirements.txt
pip install python-dotenv

cd ..

echo [3/4] Setting up Frontend (Node.js)...
cd frontend
if not exist node_modules (
    echo Installing npm packages...
    call npm install
) else (
    echo node_modules already exists. Skipping npm install.
)
cd ..

echo [4/4] Installation Complete!
echo.
echo You can now run 'start-app.bat' to launch the project.
pause
