@echo off
TITLE DESINSTALADOR DE SERVICIO SERTEC - TI
SETLOCAL ENABLEDELAYEDEXPANSION
COLOR 0C

:: Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Debes ejecutar este script como ADMINISTRADOR.
    pause
    exit /b 1
)

echo ============================================================
echo      DESINSTALACION DE SERVICIO - SERTEC SYSTEM
echo ============================================================
echo.

:: 1. Detener y eliminar procesos de PM2
echo [INFO] Deteniendo y eliminando procesos de Sertec en PM2...
call pm2 stop sertec-server sertec-tunnel >nul 2>&1
call pm2 delete sertec-server sertec-tunnel >nul 2>&1
call pm2 save

:: 2. Eliminar el inicio automatico de Windows
echo [INFO] Eliminando el servicio de arranque de Windows...
call pm2-startup uninstall

echo.
echo ============================================================
echo      DESINSTALACION COMPLETADA
echo ============================================================
echo El sistema SERTEC ya no se iniciara automaticamente con Windows.
echo Los servicios han sido removidos con exito.
echo ============================================================
echo.
pause
