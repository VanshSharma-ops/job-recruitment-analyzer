@echo off
cd /d "%~dp0"
echo Pushing Job Recruitment Analyzer to https://github.com/VanshSharma-ops/job-recruitment-analyzer ...
git push -u origin main
echo.
echo If it succeeded, check your GitHub repo at:
echo https://github.com/VanshSharma-ops/job-recruitment-analyzer
echo.
pause
