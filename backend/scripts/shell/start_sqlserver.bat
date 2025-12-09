@echo off
echo ========================================
echo    INICIANDO SERVIDOR CON SQL SERVER
echo ========================================
echo.

REM Configurar variable de entorno para SQL Server
set DJANGO_SETTINGS_MODULE=postventa_system.settings-sqlserver

echo Configuracion: %DJANGO_SETTINGS_MODULE%
echo Base de datos: SQL Server Express
echo Servidor: NB-JDIAZ25\SQLEXPRESS
echo Base de datos: postventa_system
echo.

REM Iniciar servidor Django
echo Iniciando servidor Django...
python manage.py runserver 8000

pause
