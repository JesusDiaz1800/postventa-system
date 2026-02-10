@echo off
title Postventa System - PM2 Manager
color 0A

REM ==============================================================================
REM  POSTVENTA SYSTEM - Professional Process Manager
REM  
REM  Este script usa PM2 para manejar los procesos del sistema.
REM  PM2 mantiene los procesos vivos, reinicia automaticamente si fallan,
REM  y proporciona logs unificados.
REM ==============================================================================

set PM2_PATH=C:\Users\jdiaz\AppData\Roaming\npm\pm2.cmd
set PROJECT_PATH=%~dp0

echo.
echo ========================================
echo   SISTEMA POSTVENTA - PM2 MANAGER
echo ========================================
echo.

REM Detectar IP actual con ruta completa a ipconfig
set CURRENT_IP=localhost
for /f "tokens=2 delims=:" %%a in ('C:\Windows\System32\ipconfig.exe 2^>nul ^| C:\Windows\System32\findstr.exe /c:"IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do set CURRENT_IP=%%b
)
echo IP Detectada: %CURRENT_IP%
echo.

if "%1"=="start" goto :start
if "%1"=="stop" goto :stop
if "%1"=="restart" goto :restart
if "%1"=="status" goto :status
if "%1"=="logs" goto :logs
if "%1"=="monit" goto :monit
if "%1"=="menu" goto :menu

REM Por defecto iniciar directamente (Autoinicio)
goto :start

:menu
echo Comandos disponibles:
echo   INICIAR_PM2.bat start    - Iniciar todos los servicios
echo   INICIAR_PM2.bat stop     - Detener todos los servicios
echo   INICIAR_PM2.bat restart  - Reiniciar todos los servicios
echo   INICIAR_PM2.bat status   - Ver estado de los servicios
echo   INICIAR_PM2.bat logs     - Ver logs en tiempo real
echo   INICIAR_PM2.bat monit    - Dashboard de monitoreo
echo.
echo Seleccione una opcion:
echo   [1] Iniciar sistema
echo   [2] Detener sistema
echo   [3] Ver estado
echo   [4] Ver logs
echo   [5] Monitoreo (dashboard)
echo   [6] Salir
echo.
set /p choice="Opcion: "

if "%choice%"=="1" goto :start
if "%choice%"=="2" goto :stop
if "%choice%"=="3" goto :status
if "%choice%"=="4" goto :logs
if "%choice%"=="5" goto :monit
if "%choice%"=="6" exit /b 0
goto :menu

:start
echo.
echo [*] Iniciando servicios con PM2...
cd /d "%PROJECT_PATH%"

REM Primero eliminar procesos existentes para evitar conflictos
echo [*] Limpiando procesos anteriores...
call "%PM2_PATH%" delete all 2>nul

REM Ahora iniciar fresh
echo [*] Iniciando servicios frescos...
call "%PM2_PATH%" start ecosystem.config.js

if %ERRORLEVEL% neq 0 (
    echo.
    echo [!] Error al iniciar. Intentando reiniciar PM2 daemon...
    call "%PM2_PATH%" kill 2>nul
    timeout /t 2 /nobreak >nul
    call "%PM2_PATH%" start ecosystem.config.js
)

echo.
echo ========================================
echo   SISTEMA INICIADO CORRECTAMENTE
echo ========================================
echo.
echo Acceso al sistema:
echo   Frontend: https://%CURRENT_IP%:5173
echo   Backend:  http://%CURRENT_IP%:8000
echo.
echo Comandos utiles:
echo   INICIAR_PM2.bat logs    - Ver logs en tiempo real
echo   INICIAR_PM2.bat status  - Ver estado
echo   INICIAR_PM2.bat stop    - Detener
echo.
pause
exit /b 0

:stop
echo.
echo [*] Deteniendo servicios...
call "%PM2_PATH%" stop all 2>nul
call "%PM2_PATH%" delete all 2>nul
echo.
echo Servicios detenidos y eliminados.
pause
exit /b 0

:restart
echo.
echo [*] Reiniciando servicios...
cd /d "%PROJECT_PATH%"

REM Clean restart: delete and start fresh
call "%PM2_PATH%" delete all 2>nul
call "%PM2_PATH%" start ecosystem.config.js

echo.
echo Servicios reiniciados.
pause
exit /b 0

:status
echo.
call "%PM2_PATH%" status
echo.
pause
exit /b 0

:logs
echo.
echo [*] Mostrando logs en tiempo real (Ctrl+C para salir)...
call "%PM2_PATH%" logs
exit /b 0

:monit
echo.
echo [*] Abriendo dashboard de monitoreo...
call "%PM2_PATH%" monit
exit /b 0
