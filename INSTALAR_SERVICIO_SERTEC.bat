@echo off
TITLE INSTALADOR DE PERSISTENCIA EMPRESARIAL (SERTEC SYSTEM) - TI
SETLOCAL ENABLEDELAYEDEXPANSION
COLOR 0B

echo ============================================================
echo      CONFIGURACION DE ARRANQUE EMPRESARIAL (SERTEC SYSTEM)
echo ============================================================
echo.

:: 1. Verificar permisos de administrador
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Debes ejecutar este script como ADMINISTRADOR.
    echo Por favor, haz clic derecho sobre este archivo y selecciona "Ejecutar como administrador".
    echo.
    pause
    exit /b 1
)
echo [OK] Permisos de administrador detectados.

:: 2. Verificar Node.js
where node >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Node.js no esta instalado globalmente.
    echo Es un requisito obligatorio para gestionar los procesos con PM2.
    echo Por favor, instale Node.js (LTS) desde: https://nodejs.org/
    echo.
    pause
    exit /b 1
)
echo [OK] Node.js detectado en el sistema.

:: 3. Instalar PM2 globalmente si no existe
where pm2 >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Instalando PM2 globalmente en el servidor...
    call npm install pm2 -g
) else (
    echo [OK] PM2 ya se encuentra instalado.
)

:: 4. Instalar pm2-windows-startup para arranque a nivel de Kernel
echo [INFO] Instalando y configurando pm2-windows-startup...
call npm install pm2-windows-startup -g
call pm2-startup install
echo [OK] Arranque de PM2 registrado en el Registro de Windows.

:: 5. Asegurar compilacion de Frontend de Produccion
if not exist "frontend\dist" (
    echo [WARNING] Carpeta frontend\dist no encontrada.
    echo [INFO] Compilando frontend para produccion (esto puede tardar 1-2 minutos)...
    cd frontend
    call npm install
    call npm run build
    cd ..
) else (
    echo [OK] Compilacion estatica detectada en frontend\dist.
)

:: 6. Detener procesos existentes para evitar colisiones
echo [INFO] Limpiando procesos previos de Sertec en PM2...
call pm2 delete sertec-server >nul 2>&1
call pm2 delete sertec-tunnel >nul 2>&1

:: 7. Iniciar con el ecosistema de produccion unificado (Puerto 8001)
echo [INFO] Registrando y arrancando servicios en PM2...
call pm2 start ecosystem.config.js
if %errorLevel% neq 0 (
    echo [ERROR] Error al arrancar ecosystem.config.js con PM2.
    pause
    exit /b 1
)

:: 8. Congelar la configuracion
echo [INFO] Guardando dump de procesos para reinicio automatico...
call pm2 save
if %errorLevel% neq 0 (
    echo [ERROR] No se pudo guardar la lista de procesos con 'pm2 save'.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo      INSTALACION Y CONFIGURACION COMPLETADA EXITOSAMENTE
echo ============================================================
echo El sistema SERTEC ahora operara como un SERVICIO RESILIENTE.
echo.
echo CARACTERISTICAS DEL SERVICIO:
echo 1. Se inicia automaticamente con Windows (antes del login de usuario).
echo 2. Se reiniciara solo ante caidas de red o fallas internas de software.
echo 3. Mantiene el puerto unificado 8001 activo y el tunel seguro levantado.
echo.
echo COMANDOS UTILES PARA EL PERSONAL DE TI:
echo - Ver procesos en linea:  pm2 status
echo - Ver logs en tiempo real: pm2 logs
echo - Reiniciar todo:          pm2 restart all
echo - Detener servicio:        pm2 stop all
echo ============================================================
echo.
pause
