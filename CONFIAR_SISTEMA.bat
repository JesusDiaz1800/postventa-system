@echo off
:: CONFIAR_SISTEMA.bat - Configuración Automatizada de Seguridad Postventa
:: Polifusion S.A. - Departamento de Sistemas

:: Asegurar que trabajamos en la carpeta del script (ayuda si se ejecuta como admin)
cd /d "%~dp0"

set "CA_CERT=%~dp0frontend\ssl\poly-ca-cert.pem"
set "HOSTNAME=postventa.local"
set "SERVER_IP=192.168.1.234"

title Configurar Acceso Seguro - Sistema Postventa
color 0A

echo ============================================================
echo   CONFIGURACION DE SEGURIDAD Y ACCESO - SISTEMA POSTVENTA
echo   Polifusion S.A.
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

:: 2. Instalar Certificado Raiz de Polifusion
echo [1/3] Instalando Certificado de Confianza Polifusion...
if not exist "%CA_CERT%" (
    echo [ERROR] No se encuentra el archivo de seguridad en:
    echo %CA_CERT%
    echo.
    echo Por favor, asegurese de que el servidor este bien configurado.
    pause
    exit /b 1
)

certutil -addstore -f "Root" "%CA_CERT%" >nul
if %errorLevel% equ 0 (
    echo [OK] El sistema ahora confia en el servidor de Postventa.
) else (
    echo [ERROR] No se pudo instalar el certificado.
)

:: 3. Configurar Hostname Local (archivo hosts)
echo [2/3] Configurando nombre de red 'https://%HOSTNAME%'...
set "HOSTS_FILE=%SystemRoot%\System32\drivers\etc\hosts"

:: Eliminar entrada anterior si existe para evitar duplicados
findstr /v "%HOSTNAME%" "%HOSTS_FILE%" > "%TEMP%\hosts_new"
echo %SERVER_IP% %HOSTNAME% >> "%TEMP%\hosts_new"

:: Mover el nuevo archivo a su lugar
move /y "%TEMP%\hosts_new" "%HOSTS_FILE%" >nul

if %errorLevel% equ 0 (
    echo [OK] Nombre de red '%HOSTNAME%' apuntando a %SERVER_IP%.
    ipconfig /flushdns >nul
) else (
    echo [ERROR] No se pudo escribir en el archivo hosts. 
    echo Verifique que no tenga un Antivirus bloqueando el archivo.
)

:: 4. Finalizacion
echo [3/3] Operacion completada con exito.
echo.
echo ============================================================
echo   ¡CONFIGURACION EXITOSA!
echo ============================================================
echo.
echo   1. El sistema ahora es reconocido como SEGURO.
echo   2. El nombre 'postventa.local' esta ACTIVO.
echo.
echo   URL: https://%HOSTNAME%:5173
echo ============================================================
echo.
echo Presione cualquier tecla para abrir el sistema...
pause
start https://%HOSTNAME%:5173
exit /b 0
