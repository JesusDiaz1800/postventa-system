@echo off
TITLE INSTALADOR DE SERVICIO SERTEC - TI
SETLOCAL ENABLEDELAYEDEXPANSION

:: ============================================================
::      CONFIGURACION DE PERSISTENCIA - SERTEC SYSTEM
:: ============================================================
:: Este script configurara la aplicacion para que:
:: 1. Se inicie automaticamente con Windows (sin login de usuario)
:: 2. Se reinicie sola si hay un crash.
:: 3. Mantenga el tunel de internet siempre activo.
:: ============================================================

:: 1. Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Debes ejecutar este script como ADMINISTRADOR.
    echo Haz clic derecho sobre el archivo y selecciona "Ejecutar como administrador".
    pause
    exit /b 1
)

echo [OK] Permisos de administrador detectados.
echo.

:: 2. Verificar dependencias criticas
where node >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Node.js no esta instalado. Es necesario para gestionar los servicios.
    echo Por favor, instale Node.js (LTS) desde https://nodejs.org/
    pause
    exit /b 1
)

:: 3. Instalar/Verificar PM2
where pm2 >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Instalando PM2 (Process Manager 2) globalmente...
    call npm install pm2 -g
    if %errorLevel% neq 0 (
        echo [ERROR] No se pudo instalar PM2. Verifique su conexion a internet.
        pause
        exit /b 1
    )
) else (
    echo [OK] PM2 ya esta instalado.
)

:: 4. Instalar gestor de arranque para Windows
:: Este paquete permite que PM2 se registre como un servicio de Windows
echo [INFO] Configurando el inicio automatico con Windows...
call npm install pm2-windows-startup -g
if %errorLevel% neq 0 (
    echo [ERROR] No se pudo instalar pm2-windows-startup.
    pause
    exit /b 1
)

:: Registrar el servicio de PM2
call pm2-startup install
if %errorLevel% neq 0 (
    echo [INFO] Si pm2-startup ya estaba instalado, esto es normal. Continuando...
)

:: 5. Asegurar que el Frontend este compilado (Produccion)
if not exist "frontend\dist" (
    echo [WARNING] No se detecto la carpeta 'frontend\dist'. 
    echo [INFO] Compilando frontend para produccion...
    cd frontend
    call npm install
    call npm run build
    cd ..
)

:: 6. Limpiar procesos previos de Sertec (evitar duplicados)
echo [INFO] Limpiando procesos antiguos...
call pm2 delete sertec-server >nul 2>&1
call pm2 delete sertec-tunnel >nul 2>&1

:: 7. Iniciar la aplicacion usando el archivo de ecosistema
echo [INFO] Iniciando servicios de Sertec (Servidor + Tunel)...
call pm2 start ecosystem.config.js
if %errorLevel% neq 0 (
    echo [ERROR] Error al iniciar los procesos con PM2. Verifique ecosystem.config.js.
    pause
    exit /b 1
)

:: 8. Congelar la configuracion para el arranque
:: Esto asegura que lo que esta corriendo ahora se inicie al reiniciar el servidor
echo [INFO] Guardando lista de procesos para el proximo reinicio...
call pm2 save
if %errorLevel% neq 0 (
    echo [ERROR] No se pudo guardar la configuracion de PM2.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo      INSTALACION COMPLETADA EXITOSAMENTE
echo ============================================================
echo El sistema SERTEC ahora es un SERVICIO RESILIENTE.
echo.
echo COMANDOS UTILES PARA TI:
echo - Ver estado: pm2 status
echo - Ver logs:   pm2 logs
echo - Reiniciar:  pm2 restart all
echo - Detener:    pm2 stop all
echo ============================================================
pause
