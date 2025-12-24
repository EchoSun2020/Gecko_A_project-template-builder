@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo   Git Push Script
echo ========================================
echo.

set /p MSG="Commit message (or press Enter for default): "
if "%MSG%"=="" set MSG=update

echo.
echo [INFO] Adding files...
git add .

echo [INFO] Committing...
git commit -m "%MSG%"

echo [INFO] Pushing to GitHub...
git push --set-upstream origin main --force

echo.
echo ========================================
echo [DONE] Push complete!
echo ========================================
pause

