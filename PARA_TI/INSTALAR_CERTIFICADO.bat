@echo off
:: INSTALAR_CERTIFICADO.bat - Para uso exclusivo de TI
:: Polifusion S.A. - Sistema de Postventa

:: Asegurar que trabajamos en la carpeta del script
cd /d "%~dp0"

set "CA_CERT=%~dp0poly-ca-cert.pem"

title Instalacion de Certificado - Sistema Postventa
color 0B

echo ============================================================
echo   INSTALACION DE CERTIFICADO DE SEGURIDAD
echo   Sistema de Postventa - Polifusion S.A.
echo   (Solo para uso de TI)
echo ============================================================
echo.

:: 1. Verificar privilegios de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Se requieren permisos de Administrador.
    echo.
    echo Por favor:
    echo 1. Haga clic DERECHO sobre este archivo.
    echo 2. Seleccione "Ejecutar como administrador".
    echo.
    pause
    exit /b 1
)

:: 2. Verificar certificado
if not exist "%CA_CERT%" (
    echo [ERROR] No se encuentra el certificado 'poly-ca-cert.pem'.
    echo Por favor copie toda la carpeta PARA_TI correctamente.
    pause
    exit /b 1
)

:: 3. Instalar Certificado Raiz
echo [1/1] Instalando Certificado de Confianza Polifusion...
certutil -addstore -f "Root" "%CA_CERT%" >nul

if %errorLevel% equ 0 (
    echo.
    echo ============================================================
    echo   EXITOSO - CERTIFICADO INSTALADO CORRECTAMENTE
    echo ============================================================
    echo.
    echo   Este PC ahora confia en el Sistema de Postventa.
    echo.
    echo   El usuario puede acceder a:
    echo   https://192.168.1.234:5173
    echo.
    echo   (Sin advertencias de seguridad)
    echo ============================================================
) else (
    echo.
    echo [ERROR CRITICO] No se pudo instalar el certificado.
    echo Codigo de error: %errorLevel%
    echo.
    echo Verifique:
    echo 1. Que ejecuto como ADMINISTRADOR.
    echo 2. Que el archivo poly-ca-cert.pem esta en la misma carpeta.
    echo.
)

echo.
echo Presione una tecla para salir...
pause >nul
exit /b 0
