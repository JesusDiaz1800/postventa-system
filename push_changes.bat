@echo off
echo ========================================
echo    SUBIENDO CAMBIOS A GITHUB
echo ========================================
echo.

cd C:\Users\Jesus Diaz\postventa-system

echo Agregando cambios...
git add .

echo.
echo Ingresa un mensaje para el commit:
set /p commit_message="Mensaje: "

echo.
echo Haciendo commit...
git commit -m "%commit_message%"

echo.
echo Subiendo cambios a GitHub...
git push

echo.
echo Cambios subidos exitosamente!
echo.
pause
