@echo off
title Detener Sistema PostVenta
color 0C

echo.
echo ========================================
echo   DETENIENDO SISTEMA POSTVENTA
echo ========================================
echo.

echo [1/3] Deteniendo Backend Django...
taskkill /f /im python.exe >nul 2>&1
if errorlevel 1 (
    echo No hay procesos Python ejecutandose
) else (
    echo Backend Django detenido
)

echo.
echo [2/3] Deteniendo Frontend React...
taskkill /f /im node.exe >nul 2>&1
if errorlevel 1 (
    echo No hay procesos Node ejecutandose
) else (
    echo Frontend React detenido
)

echo.
echo [3/3] Verificando detencion...
timeout /t 2 >nul
tasklist /fi "imagename eq python.exe" 2>nul | find /i "python.exe" >nul
if not errorlevel 1 (
    echo WARNING: Aun hay procesos Python ejecutandose
) else (
    echo OK: Todos los procesos Python detenidos
)

tasklist /fi "imagename eq node.exe" 2>nul | find /i "node.exe" >nul
if not errorlevel 1 (
    echo WARNING: Aun hay procesos Node ejecutandose
) else (
    echo OK: Todos los procesos Node detenidos
)

echo.
echo ========================================
echo   SISTEMA DETENIDO COMPLETAMENTE
echo ========================================
echo.
echo Para reiniciar el sistema:
echo   INICIAR_SISTEMA_PRODUCCION.bat
echo.
pause
