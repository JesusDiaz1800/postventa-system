@echo off
title Sistema PostVenta
color 0A
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   SISTEMA POSTVENTA - INICIO
echo ========================================
echo.

REM Detectar IP actual
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=1" %%b in ("%%a") do set CURRENT_IP=%%b
)
if not defined CURRENT_IP set CURRENT_IP=localhost
echo IP Detectada: %CURRENT_IP%
echo.

echo [1/4] Limpiando procesos anteriores...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo Procesos anteriores detenidos.

echo.
echo [2/4] Verificando dependencias...
if not exist "python-portable\python\python.exe" (
    echo ERROR: Python portable no encontrado
    echo Instale Python portable en la carpeta python-portable
    pause
    exit /b 1
)

if not exist "frontend\node_modules" (
    echo ERROR: Node modules no encontrados
    echo Ejecute: cd frontend ^&^& npm install
    pause
    exit /b 1
)

echo Dependencias verificadas.

echo.
echo [3/4] Iniciando Backend Django con ASGI...
echo Backend: http://%CURRENT_IP%:8000
echo WebSocket: ws://%CURRENT_IP%:8000/ws/notifications/
start "Backend Django ASGI" cmd /k "cd backend && ..\python-portable\python\python.exe -m daphne -b 0.0.0.0 -p 8000 postventa_system.asgi:application"

echo Esperando 5 segundos para que el backend ASGI inicie...
ping 127.0.0.1 -n 6 >nul

echo.
echo [4/4] Iniciando Frontend React...
echo Frontend: http://%CURRENT_IP%:5173
cd frontend
start "Frontend React" cmd /k "npm run dev -- --host 0.0.0.0"
cd ..

echo.
echo ========================================
echo   SISTEMA INICIADO
echo ========================================
echo.
echo ACCESO AL SISTEMA:
echo   URL: https://%CURRENT_IP%:5173
echo   (O desde esta PC: https://localhost:5173)
echo.
echo CREDENCIALES PRINCIPALES:
echo   Usuario: jdiaz
echo   Password: adminJDR
echo.
echo OTROS USUARIOS DISPONIBLES:
echo   pestay / Pestay2025!
echo   pmorales / Patricio2025!
echo   mmontenegro / Marco2025!
echo.
echo CONFIGURACION ASGI:
echo   Backend: Django + Daphne (ASGI)
echo   Frontend: React + Vite
echo   WebSocket: Habilitado
echo.
echo ========================================
echo   SISTEMA LISTO CON WEBSOCKET
echo ========================================
echo.
echo Para detener el sistema:
echo   taskkill /f /im python.exe
echo   taskkill /f /im node.exe
echo.
echo Presiona cualquier tecla para cerrar...
pause >nul
