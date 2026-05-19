@echo off
TITLE SERTEC SYSTEM - MASTER STARTUP
COLOR 0B

echo ========================================================
echo        S E R T E C   S Y S T E M   -   V 2.0
echo ========================================================
echo.

set BASE_DIR=%~dp0

:: 1. Lanzar Backend (Django)
echo [+] Lanzando BACKEND (Puerto 8001)...
start "SERTEC BACKEND" /min cmd /c "cd /d %BASE_DIR%\backend && ..\python312\Scripts\daphne.exe -b 0.0.0.0 -p 8001 postventa_system.asgi:application"

:: 2. Lanzar Frontend (Vite)
echo [+] Lanzando FRONTEND (Vite)...
start "SERTEC FRONTEND" /min cmd /c "cd /d %BASE_DIR%\frontend && npm run dev"

:: 3. Lanzar Túnel Cloudflare (Si existe configuración)
if exist "%BASE_DIR%\cloudflare_sertec.yml" (
    echo [+] Lanzando TÚNEL CLOUDFLARE...
    start "SERTEC TUNNEL" /min cmd /c "cloudflared.exe tunnel --config %BASE_DIR%\cloudflare_sertec.yml run sertec"
)

echo.
echo ========================================================
echo    ¡TODO LANZADO! Los servidores estan en segundo plano.
echo    - Backend: http://localhost:8001
echo    - Frontend: http://localhost:5173
echo    - Web: https://sertec.polifusion.com
echo ========================================================
echo.
echo Presione cualquier tecla para cerrar esta ventana (Los servidores seguiran activos).
pause > nul
exit
