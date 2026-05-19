@echo off
title INICIAR SISTEMA SERTEC - PRODUCCION
echo ========================================================
echo    INICIANDO SISTEMA SERTEC (MODO PRODUCCION INDEPENDIENTE)
echo ========================================================

:: --- RUTAS ABSOLUTAS (ESTRICTAMENTE SERTEC-SYSTEM) ---
set ROOT_DIR=C:\Users\jdiaz\Desktop\sertec-system
set PM2_PATH=C:\Users\jdiaz\AppData\Roaming\npm\pm2.cmd
set CLOUDFLARED_PATH=%ROOT_DIR%\cloudflared.exe
set PYTHON_DIR=%ROOT_DIR%\python-portable
set DAPHNE_PATH=%PYTHON_DIR%\Scripts\daphne.exe
set BACKEND_DIR=%ROOT_DIR%\backend

:: Limpiar path temporalmente para este script para evitar conflictos
set PATH=%PYTHON_DIR%;%PYTHON_DIR%\Scripts;%PATH%

:: 1. Limpiar SOLO los procesos de Sertec
echo [1/3] Limpiando procesos de Sertec previos...
call "%PM2_PATH%" delete sertec-server sertec-tunnel 2>nul

:: 2. Iniciar el Tunel de Cloudflare
echo [2/3] Levantando Tunel de Cloudflare...
call "%PM2_PATH%" start "%CLOUDFLARED_PATH%" --name sertec-tunnel -- tunnel run sertec-tunnel

:: 3. Iniciar el Servidor Daphne desde la carpeta BACKEND de SERTEC
echo [3/3] Iniciando Servidor Daphne (Backend)...
cd /d "%BACKEND_DIR%"
:: Usamos el ejecutable de daphne de la carpeta sertec-system explicitamente
call "%PM2_PATH%" start "%DAPHNE_PATH%" --name sertec-server --cwd "%BACKEND_DIR%" -- -p 8001 -b 0.0.0.0 --proxy-headers postventa_system.asgi:application

:: Guardar estado
call "%PM2_PATH%" save

echo ========================================================
echo    SERTEC SISTEMA INICIADO EN SU PROPIO ENTORNO
echo    Dominio: https://sertec.polifusion.com
echo ========================================================
call "%PM2_PATH%" status
pause
