@echo off
TITLE SERTEC SYSTEM - CONTROLADOR DE DESPLIEGUE UNIFICADO
COLOR 0B

:: --- CONFIGURACION DE RUTAS ---
set ROOT_DIR=%~dp0
if "%ROOT_DIR:~-1%"=="\" set ROOT_DIR=%ROOT_DIR:~0,-1%
set BACKEND_DIR=%ROOT_DIR%\backend
set CLOUDFLARED_EXE=%ROOT_DIR%\cloudflared.exe
set CONFIG_YML=%ROOT_DIR%\sertec_config.yml
set PM2_PATH=C:\Users\jdiaz\AppData\Roaming\npm\pm2.cmd

echo ========================================================
echo        SERTEC SYSTEM - MOTOR DE PRODUCCION UNIFICADO
echo ========================================================
echo.
echo [1/4] Liberando puertos de Sertec...

:: Liberar selectivamente puerto 8001
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8001" ^| findstr "LISTENING"') do (
    echo [INFO] Puerto 8001 ocupado. Finalizando proceso PID %%a...
    taskkill /f /pid %%a >nul 2>&1
)

:: Liberar selectivamente puerto 5174 (Desarrollo)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5174" ^| findstr "LISTENING"') do (
    echo [INFO] Puerto 5174 ocupado. Finalizando proceso PID %%a...
    taskkill /f /pid %%a >nul 2>&1
)

echo [OK] Puertos de Sertec liberados.
echo [OK] Puertos de Incidencias (8000/5173) intactos y seguros.
echo.

:: Detectar Python y Daphne en entornos portables
set PYTHON_EXE=
set DAPHNE_EXE=
if exist "%ROOT_DIR%\python-portable\python\python.exe" (
    set PYTHON_EXE=%ROOT_DIR%\python-portable\python\python.exe
    set DAPHNE_EXE=%ROOT_DIR%\python-portable\python\Scripts\daphne.exe
)
if not exist "%DAPHNE_EXE%" if exist "%ROOT_DIR%\python312\python.exe" (
    set PYTHON_EXE=%ROOT_DIR%\python312\python.exe
    set DAPHNE_EXE=%ROOT_DIR%\python312\Scripts\daphne.exe
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] No se encuentra el motor de Python en las rutas esperadas.
    pause
    exit /b 1
)

echo [2/4] Verificando compilacion de Frontend estatico...
if not exist "%ROOT_DIR%\frontend\dist" (
    echo [WARNING] No se detecto la carpeta 'frontend\dist'.
    echo [INFO] Compilando frontend para produccion...
    cd /d "%ROOT_DIR%\frontend"
    call npm run build
    cd /d "%ROOT_DIR%"
) else (
    echo [OK] Compilacion estatica de produccion existente.
)
echo.

echo [3/4] Determinando metodo de arranque óptimo...
where pm2 >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] PM2 detectado. Iniciando en segundo plano de manera resiliente...
    call "%PM2_PATH%" delete sertec-server sertec-tunnel >nul 2>&1
    call "%PM2_PATH%" start ecosystem.config.js
    call "%PM2_PATH%" save
    
    echo.
    echo ========================================================
    echo    SISTEMA SERTEC ACTIVO (PUERTO UNICO: 8001)
    echo    Dominio: https://sertec.polifusion.com
    echo ========================================================
    echo Los servicios corren en segundo plano gestionados por PM2:
    echo - sertec-server: Daphne sirviendo backend y frontend (Puerto 8001)
    echo - sertec-tunnel: Tunel de Cloudflare hacia internet
    echo.
    echo Comandos de utilidad:
    echo   - Ver estado: pm2 status
    echo   - Ver logs:   pm2 logs
    echo.
) else (
    echo [INFO] PM2 no instalado. Iniciando servidor en primer plano...
    echo.
    echo [4/4] Lanzando daphne en puerto 8001 y tunel Cloudflare...
    
    :: Iniciar Daphne en ventana nueva
    set PYTHONPATH=%BACKEND_DIR%
    start "SERVIDOR_SERTEC_PRODUCCION" /d "%BACKEND_DIR%" cmd /k ""%DAPHNE_EXE%" -p 8001 -b 0.0.0.0 --proxy-headers postventa_system.asgi:application"
    
    :: Iniciar Tunel en ventana nueva
    start "TUNEL_SERTEC_CLOUDFLARE" /d "%ROOT_DIR%" "%CLOUDFLARED_EXE%" --config "%CONFIG_YML%" tunnel run sertec-tunnel
    
    echo.
    echo ========================================================
    echo    SISTEMA SERTEC ACTIVO Y EN LINEA
    echo    Dominio: https://sertec.polifusion.com
    echo ========================================================
    echo Corriendo en 2 ventanas independientes (Daphne Puerto 8001 + Tunel).
    echo.
)

pause
