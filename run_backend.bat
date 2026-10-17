@echo off
cd /d "%~dp0"
echo Starting Job Recruitment Analyzer Backend on http://localhost:8000 ...
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000
pause
