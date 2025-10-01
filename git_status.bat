@echo off
echo ========================================
echo    ESTADO DEL REPOSITORIO GIT
echo ========================================
echo.

cd C:\Users\Jesus Diaz\postventa-system

echo Estado actual:
git status

echo.
echo Historial reciente:
git log --oneline -5

echo.
pause
