@echo off
title Sistema PostVenta - ASGI Completo
color 0A
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   SISTEMA POSTVENTA - ASGI COMPLETO
echo ========================================
echo.

echo [1/5] Limpiando procesos anteriores...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1
echo Procesos anteriores detenidos.

echo.
echo [2/5] Verificando dependencias...
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
echo [3/5] Iniciando Backend Django con ASGI...
echo Backend: http://192.168.1.234:8000
echo WebSocket: ws://192.168.1.234:8000/ws/notifications/
echo Base de datos: SQL Server Express (192.168.1.124:1433)
start "Backend Django ASGI" cmd /k "cd backend && ..\python-portable\python\python.exe -m daphne -b 0.0.0.0 -p 8000 postventa_system.asgi:application"

echo Esperando 10 segundos para que el backend ASGI inicie...
ping 127.0.0.1 -n 11 >nul

echo.
echo [4/5] Verificando conexion al backend ASGI...
python-portable\python\python.exe -c "import requests; r = requests.get('http://192.168.1.234:8000/', timeout=5); print('Backend ASGI Status:', r.status_code)" 2>nul
if errorlevel 1 (
    echo WARNING: Backend ASGI puede estar iniciando...
)

echo.
echo [5/5] Iniciando Frontend React...
echo Frontend: http://192.168.1.234:5173
cd frontend
start "Frontend React" cmd /k "npm run dev -- --host 0.0.0.0"
cd ..

echo.
echo ========================================
echo   SISTEMA INICIADO - ASGI COMPLETO
echo ========================================
echo.
echo ACCESO AL SISTEMA:
echo   URL: http://192.168.1.234:5173
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
echo   Base de datos: SQL Server Express
echo.
echo ========================================
echo   SISTEMA LISTO CON WEBSOCKET
echo ========================================
echo.
echo Para verificar el sistema completo:
echo   python-portable\python\python.exe VERIFICAR_SISTEMA_COMPLETO.py
echo.
echo Para verificar solo WebSocket:
echo   python-portable\python\python.exe test-websocket-complete.py
echo.
echo Para detener el sistema:
echo   taskkill /f /im python.exe
echo   taskkill /f /im node.exe
echo.
echo Presiona cualquier tecla para cerrar...
pause >nul
