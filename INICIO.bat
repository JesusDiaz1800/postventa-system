@echo off
title Postventa System - PM2
color 0A
setlocal enabledelayedexpansion

set PM2_PATH=C:\Users\jdiaz\AppData\Roaming\npm\pm2.cmd
set PROJECT_PATH=%~dp0

echo.
echo =========================================
echo   SISTEMA POSTVENTA - INICIO CON PM2
echo =========================================
echo.

REM Detectar IP local
set CURRENT_IP=localhost
for /f "tokens=2 delims=:" %%a in ('C:\Windows\System32\ipconfig.exe 2^>nul ^| C:\Windows\System32\findstr.exe /c:"IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do set CURRENT_IP=%%b
)
echo IP Detectada: %CURRENT_IP%
echo.

REM --- Parsear argumentos ---
if "%1"=="stop"    goto :stop
if "%1"=="restart" goto :restart
if "%1"=="status"  goto :status
if "%1"=="logs"    goto :logs
if "%1"=="monit"   goto :monit

REM --- Por defecto: START ---
:start
echo [1/4] Deteniendo procesos previos (PM2 + fallback)...
call "%PM2_PATH%" delete all >nul 2>&1
C:\Windows\System32\taskkill.exe /F /IM python.exe /T >nul 2>&1
C:\Windows\System32\taskkill.exe /F /IM node.exe /T >nul 2>&1
echo OK
echo.

echo [2/4] Renovando certificado SSL...
cd /d "%PROJECT_PATH%frontend"
..\python-portable\python\python.exe generate_ssl.py
cd /d "%PROJECT_PATH%"
echo.

echo [3/4] Iniciando servicios con PM2 (ecosystem.config.js)...
call "%PM2_PATH%" start ecosystem.config.js

if %ERRORLEVEL% neq 0 (
    echo [!] Error PM2. Intentando reiniciar daemon...
    call "%PM2_PATH%" kill >nul 2>&1
    C:\Windows\System32\timeout.exe /t 2 /nobreak >nul
    call "%PM2_PATH%" start ecosystem.config.js
)
echo.

echo [4/4] Estado de los servicios:
call "%PM2_PATH%" status
echo.

echo =========================================
echo   SISTEMA INICIADO
echo =========================================
echo   Frontend : https://%CURRENT_IP%:5173
echo   Backend  : http://%CURRENT_IP%:8000
echo.
echo   Comandos utiles (desde esta carpeta):
echo     INICIO.bat logs     - Ver logs en vivo
echo     INICIO.bat status   - Estado de procesos
echo     INICIO.bat restart  - Reiniciar
echo     INICIO.bat stop     - Detener todo
echo =========================================
echo.
echo Abriendo logs en tiempo real...
C:\Windows\System32\timeout.exe /t 3 /nobreak >nul
call "%PM2_PATH%" logs
goto :eof

:stop
echo.
echo [*] Deteniendo todos los servicios...
call "%PM2_PATH%" stop all >nul 2>&1
call "%PM2_PATH%" delete all >nul 2>&1
C:\Windows\System32\taskkill.exe /F /IM python.exe /T >nul 2>&1
C:\Windows\System32\taskkill.exe /F /IM node.exe /T >nul 2>&1
echo Todos los servicios detenidos.
pause
goto :eof

:restart
echo.
echo [*] Reiniciando servicios...
cd /d "%PROJECT_PATH%frontend"
..\python-portable\python\python.exe generate_ssl.py
cd /d "%PROJECT_PATH%"
call "%PM2_PATH%" delete all >nul 2>&1
call "%PM2_PATH%" start ecosystem.config.js
call "%PM2_PATH%" status
echo Reiniciado. Abriendo logs...
C:\Windows\System32\timeout.exe /t 2 /nobreak >nul
call "%PM2_PATH%" logs
goto :eof

:status
echo.
call "%PM2_PATH%" status
echo.
pause
goto :eof

:logs
echo.
echo [*] Logs en tiempo real (Ctrl+C para salir)...
call "%PM2_PATH%" logs
goto :eof

:monit
echo.
call "%PM2_PATH%" monit
goto :eof
