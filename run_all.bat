@echo off
cd /d "%~dp0"
echo ========================================================
echo Launching Job Recruitment Analyzer (Backend + Frontend)
echo ========================================================
echo.
echo Starting Backend API server on http://localhost:8000 ...
start "Job Analyzer Backend (Port 8000)" cmd /k "cd /d "%~dp0" && .venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000"

echo Starting Frontend UI server on http://localhost:5173 ...
start "Job Analyzer Frontend (Port 5173)" cmd /k "cd /d "%~dp0frontend" && "C:\Program Files\nodejs\npm.cmd" run dev"

echo.
echo Both servers have been launched in separate windows!
echo - Frontend Dashboard: http://localhost:5173
echo - Backend API Docs:   http://localhost:8000/docs
echo.
pause
