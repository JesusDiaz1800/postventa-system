@echo off
TITLE DETENER SISTEMA SERTEC
COLOR 0C

set PM2_PATH=C:\Users\jdiaz\AppData\Roaming\npm\pm2.cmd

echo ========================================================
echo        DETENIENDO SERVICIOS DE SERTEC SYSTEM
echo ========================================================
echo.

where pm2 >nul 2>&1
if %errorLevel% equ 0 (
    echo [INFO] Deteniendo servicios en PM2...
    call "%PM2_PATH%" stop sertec-server sertec-tunnel >nul 2>&1
    call "%PM2_PATH%" delete sertec-server sertec-tunnel >nul 2>&1
    call "%PM2_PATH%" save
    echo [OK] Procesos de PM2 eliminados.
)

echo [INFO] Liberando puertos y procesos locales...

:: Liberar selectivamente puerto 8001 (Servidor Daphne)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001" ^| findstr "LISTENING"') do (
    echo [INFO] Finalizando proceso Daphne en puerto 8001 (PID %%a)...
    taskkill /f /pid %%a >nul 2>&1
)

:: Liberar selectivamente puerto 5174 (Vite)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5174" ^| findstr "LISTENING"') do (
    echo [INFO] Finalizando proceso Vite en puerto 5174 (PID %%a)...
    taskkill /f /pid %%a >nul 2>&1
)

:: Detener cloudflared si hay instancias locales huerfanas
taskkill /f /im cloudflared.exe >nul 2>&1

echo.
echo ========================================================
echo    SISTEMA SERTEC DETENIDO COMPLETAMENTE
echo    Puertos 8001 y 5174 estan libres y disponibles.
echo    Los puertos de Incidencias (8000/5173) no fueron alterados.
echo ========================================================
echo.
pause
