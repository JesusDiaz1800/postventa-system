@echo off
:: CONFIGURAR_ACCESO.bat - Configuración de Seguridad Sistema Postventa
:: Polifusion S.A.

cd /d "%~dp0"
set "CA_CERT=%~dp0cert_seguridad.pem"
set "SERVER_IP=192.168.1.234"

title Configurar Acceso Seguro - Sistema Postventa
color 0E

echo ============================================================
echo   CONFIGURACION DE SEGURIDAD - SISTEMA POSTVENTA
echo   Polifusion S.A.
echo ============================================================
echo.

if not exist "%CA_CERT%" (
    echo [ERROR] No se encuentra el archivo de seguridad: cert_seguridad.pem
    echo Por favor, asegúrese de que el archivo esté en la misma carpeta.
    pause
    exit /b 1
)

:: Intentar primero con privilegios (para todos los usuarios de la PC)
net session >nul 2>&1
if %errorLevel% equ 0 (
    echo [INFO] Ejecutando con permisos de Administrador...
    certutil -addstore -f "Root" "%CA_CERT%" >nul
) else (
    echo [INFO] Instalando para el usuario actual (Sin requerir Admin)...
    :: El flag -user permite instalar sin ser administrador
    certutil -addstore -user -f "Root" "%CA_CERT%" >nul
)

if %errorLevel% equ 0 (
    echo [OK] El sistema ahora confía en el servidor de Postventa.
) else (
    echo [ERROR] No se pudo instalar el certificado.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   ¡CONFIGURACION COMPLETADA!
echo ============================================================
echo.
echo   1. El "Banner Rojo" de Chrome desaparecerá.
echo   2. IMPORTANTE: Cierre Chrome y vuelva a abrirlo ahora.
echo.
echo   URL del Sistema: https://%SERVER_IP%:5173
echo ============================================================
echo.
pause
start https://%SERVER_IP%:5173
exit /b 0
