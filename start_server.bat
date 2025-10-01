@echo off
echo ========================================
echo    INICIANDO SERVIDOR POSTVENTA
echo ========================================
echo.

cd /d "C:\Users\Jesus Diaz\postventa-system\backend"
echo Directorio: %CD%
echo.

set DJANGO_SETTINGS_MODULE=postventa_system.settings-sqlserver
echo Configuracion: %DJANGO_SETTINGS_MODULE%
echo.

echo Iniciando servidor en puerto 8000...
echo.
python manage.py runserver 8000

echo.
echo Servidor detenido.
pause
