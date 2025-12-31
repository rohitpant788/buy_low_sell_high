@echo off
echo ==========================================
echo      Buy Low Sell High - Git Sync
echo ==========================================

echo [1/4] Pulling latest changes from remote 'main'...
git pull origin main

echo.
echo [2/4] Staging all local changes...
git add .

echo.
echo [3/4] Committing changes...
set /p msg="Enter commit message (Press Enter for 'Auto-sync update'): "
if "%msg%"=="" set msg=Auto-sync update
git commit -m "%msg%"

echo.
echo [4/4] Pushing to remote 'main'...
git push origin main

echo.
echo ==========================================
echo             Sync Complete!
echo ==========================================
pause
