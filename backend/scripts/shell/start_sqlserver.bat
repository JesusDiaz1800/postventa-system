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

REM Iniciar servidor con Daphne (ASGI + WebSocket)
echo Iniciando servidor Daphne (ASGI + WebSocket)...
python -m daphne -b 0.0.0.0 -p 8000 postventa_system.asgi:application

pause
