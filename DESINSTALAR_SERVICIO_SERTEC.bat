@echo off
TITLE DESINSTALADOR DE SERVICIO SERTEC - TI
SETLOCAL ENABLEDELAYEDEXPANSION

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
echo [INFO] Deteniendo procesos activos...
call pm2 stop all
call pm2 delete all

:: 2. Eliminar el inicio automatico de Windows
echo [INFO] Eliminando el servicio de arranque de Windows...
call pm2-startup uninstall

:: 3. Limpiar configuracion guardada
echo [INFO] Limpiando dump de PM2...
if exist "%HOMEDRIVE%%HOMEPATH%\.pm2\dump.pm2" (
    del "%HOMEDRIVE%%HOMEPATH%\.pm2\dump.pm2"
)

echo.
echo ============================================================
echo      DESINSTALACION COMPLETADA
echo ============================================================
echo El sistema SERTEC ya no se iniciara automaticamente con Windows.
echo Los procesos han sido detenidos.
echo ============================================================
pause
