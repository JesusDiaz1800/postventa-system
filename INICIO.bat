@echo off
title Postventa System - Control Panel
color 0A
setlocal enabledelayedexpansion

set PM2_PATH=C:\Users\jdiaz\AppData\Roaming\npm\pm2.cmd
set PROJECT_PATH=%~dp0

echo.
echo ==========================================
echo   SISTEMA POSTVENTA - CONTROL DE USUARIO
echo ==========================================
echo.

REM Detectar IP local
set CURRENT_IP=localhost
for /f "tokens=2 delims=:" %%a in ('C:\Windows\System32\ipconfig.exe 2^>nul ^| C:\Windows\System32\findstr.exe /c:"IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do set CURRENT_IP=%%b
)

REM --- Parsear argumentos ---
if "%1"=="stop"    goto :stop
if "%1"=="restart" goto :restart
if "%1"=="status"  goto :status
if "%1"=="logs"    goto :logs
if "%1"=="monit"   goto :monit

REM --- Por defecto: START / REFRESH ---
:start
echo [*] Borrando procesos previos para inicio limpio...
call "%PM2_PATH%" delete all >nul 2>&1
echo [*] Iniciando servicios con PM2 (Ecosystem)...
cd /d "%PROJECT_PATH%"
call "%PM2_PATH%" start ecosystem.config.js --update-env
echo.
goto :status_msg

:stop
echo [*] Deteniendo servicios locales...
call "%PM2_PATH%" stop all
echo Servicios en pausa (PM2 activo).
pause
goto :eof

:restart
echo [*] Reiniciando aplicacion...
call "%PM2_PATH%" restart all
echo.
goto :status_msg

:status
call "%PM2_PATH%" status
pause
goto :eof

:logs
echo [*] Mostrando logs en tiempo real (Ctrl+C para salir)...
call "%PM2_PATH%" logs --lines 20
goto :eof

:monit
call "%PM2_PATH%" monit
goto :eof

:status_msg
echo ==========================================
echo   SISTEMA ACTIVO
echo ==========================================
echo   Frontend : https://%CURRENT_IP%:5173
echo   Backend  : http://%CURRENT_IP%:8000
echo.
echo   Comandos: 
echo     INICIO.bat logs    - Ver actividad
echo     INICIO.bat restart - Reiniciar rapido
echo     INICIO.bat stop    - Pausar todo
echo ==========================================
echo.
C:\Windows\System32\timeout.exe /t 5 /nobreak >nul
goto :eof
