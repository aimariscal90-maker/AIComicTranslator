@echo off
echo ============================================
echo   Starting AI Comic Translator...
echo ============================================

echo Starting Backend (FastAPI)...
start "AI Comic Backend" cmd /k "cd backend && venv\Scripts\activate && python -m uvicorn main:app --reload --port 8000"

echo Starting Frontend (Next.js)...
start "AI Comic Frontend" cmd /k "cd frontend && npm run dev"

echo Waiting for services to start...
timeout /t 5

echo Opening Browser...
start http://localhost:3000

echo Done! Both services are running in background windows.
pause
