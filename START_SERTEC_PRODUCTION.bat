@echo off
TITLE SERTEC SYSTEM - PRODUCTION SERVER
COLOR 0A

echo ========================================================
echo        SERTEC SYSTEM - ALTA DISPONIBILIDAD
echo ========================================================
echo.
echo [1/3] Verificando entorno...
set PYTHON_PATH=%~dp0python-portable\python\python.exe
set BACKEND_PATH=%~dp0backend

if not exist "%PYTHON_PATH%" (
    echo [ERROR] No se encuentra el interprete de Python en %PYTHON_PATH%
    pause
    exit /b
)

echo [2/3] Iniciando Servidor Daphne (ASGI/WebSockets)...
echo El servidor estara disponible en el puerto 8001
start "SERTEC SERVER" /min "%PYTHON_PATH%" -m daphne -p 8001 -b 0.0.0.0 postventa_system.asgi:application --root-path "%BACKEND_PATH%"

echo [3/3] Iniciando Tunel de Cloudflare...
start "SERTEC TUNNEL" /min cloudflared.exe tunnel run sertec-tunnel

echo.
echo ========================================================
echo    SISTEMA ACTIVO Y MONITOREADO
echo ========================================================
echo Los servidores se estan ejecutando en segundo plano (minimizados).
echo Para cerrar el sistema, cierre las ventanas minimizadas.
echo.
pause
