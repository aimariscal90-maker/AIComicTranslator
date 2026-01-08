@echo off
echo ========================================
echo AI Comic Translator - Backend Debug
echo ========================================
echo.
echo Starting backend with visible logs...
echo Press CTRL+C to stop
echo.

cd /d "%~dp0"
call venv\Scripts\activate
python -m uvicorn main:app --reload --port 8000

pause
