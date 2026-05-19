@echo off
title SERTEC SYSTEM - MOTOR DE PRODUCCION
color 0b

echo ========================================================
echo        SERTEC SYSTEM - INDEPENDENCIA TOTAL
echo ========================================================
echo.

:: --- RUTAS DEL SISTEMA ---
set ROOT_DIR=%~dp0
if "%ROOT_DIR:~-1%"=="\" set ROOT_DIR=%ROOT_DIR:~0,-1%
set PYTHON_EXE=%ROOT_DIR%\python312\python.exe
set DAPHNE_EXE=%ROOT_DIR%\python312\Scripts\daphne.exe
set BACKEND_DIR=%ROOT_DIR%\backend
set CLOUDFLARED_EXE=%ROOT_DIR%\cloudflared.exe
set CONFIG_YML=%ROOT_DIR%\sertec_config.yml

:: --- VALIDACION ---
if not exist "%PYTHON_EXE%" (
    echo [ERROR] No se encuentra el motor de Python en: %PYTHON_EXE%
    pause
    exit /b
)

echo [1/2] Lanzando Servidor Sertec (Daphne Port 8001)...
:: Configuramos PYTHONPATH para que Django encuentre las apps
set PYTHONPATH=%BACKEND_DIR%
start "SERVIDOR_SERTEC_PRODUCCION" /d "%BACKEND_DIR%" cmd /k ""%DAPHNE_EXE%" -p 8001 -b 0.0.0.0 --proxy-headers postventa_system.asgi:application"

echo [2/2] Lanzando Tunel Sertec en ventana independiente...
:: Lanzamos el tunel usando solo su configuracion de Sertec
start "TUNEL_SERTEC_CLOUDFLARE" /d "%ROOT_DIR%" "%CLOUDFLARED_EXE%" --config "%CONFIG_YML%" tunnel run sertec-tunnel

echo.
echo ========================================================
echo    SISTEMA SERTEC ACTIVO Y AISLADO
echo ========================================================
echo El sistema esta corriendo en dos ventanas nuevas:
echo 1. SERVIDOR_SERTEC_PRODUCCION (Puerto 8001)
echo 2. TUNEL_SERTEC_CLOUDFLARE (sertec.polifusion.com)
echo.
pause
