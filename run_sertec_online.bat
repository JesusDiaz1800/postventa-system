@echo off
TITLE SERTEC SYSTEM - ONLINE DEPLOYMENT (SUPER FLUIDO)
COLOR 0A

echo ========================================================
echo   SERTEC SYSTEM - INICIO DE ALTA DISPONIBILIDAD
echo ========================================================
echo.

set BASE_DIR=%~dp0

:: 1. Limpieza Quirúrgica (Solo puertos SERTEC: 8001 y 5174)
echo [*] Liberando puertos 8001 y 5174...
powershell -Command "$p8001 = Get-NetTCPConnection -LocalPort 8001 -ErrorAction SilentlyContinue; if($p8001) { Stop-Process -Id $p8001.OwningProcess -Force }; $p5174 = Get-NetTCPConnection -LocalPort 5174 -ErrorAction SilentlyContinue; if($p5174) { Stop-Process -Id $p5174.OwningProcess -Force }" >nul 2>&1

echo [*] Limpiando cache de desarrollo...
if exist "frontend\node_modules\.vite" rmdir /s /q "frontend\node_modules\.vite"
timeout /t 2 /nobreak >nul

:: 2. Iniciar Backend (Daphne)
echo [+] Lanzando BACKEND (Puerto 8001)...
start "SERTEC_BACKEND" /min cmd /c "cd /d %BASE_DIR%\backend && ..\python312\Scripts\daphne.exe -b 0.0.0.0 -p 8001 postventa_system.asgi:application"

:: 3. Iniciar Frontend (Vite)
echo [+] Lanzando FRONTEND (Puerto 5174)...
start "SERTEC_FRONTEND" /min cmd /c "cd /d %BASE_DIR%\frontend && npm run dev"

:: 4. Iniciar Túnel Cloudflare
echo [+] Vinculando dominio sertec.polifusion.com...
start "SERTEC_TUNNEL" /min cmd /c "cd /d %BASE_DIR% && cloudflared.exe tunnel --config cloudflare_sertec.yml run sertec"

echo.
echo ========================================================
echo   SISTEMA OPERATIVO EN: https://sertec.polifusion.com
echo ========================================================
echo.
echo Esta ventana se cerrara en 5 segundos.
timeout /t 5
exit
