@echo off
title Sistema de Postventa - Iniciar Servidores
color 0A

echo.
echo ========================================
echo    SISTEMA DE POSTVENTA - POLIFUSION
echo    Iniciar Servidores
echo ========================================
echo.

:: Verificar que estamos en la carpeta correcta
cd /d "%~dp0"

:: Verificar/crear entorno virtual de Python con Python 3.13
set "VENV_PATH=.venv"
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo No se encontro '%VENV_PATH%'. Creando entorno virtual con Python 3.13...
    py -3.13 -m venv "%VENV_PATH%"
    if errorlevel 1 (
        echo ERROR: Python 3.13 no disponible. Instale Python 3.13 x64 y reintente.
        pause
        exit /b 1
    )
)

call "%VENV_PATH%\Scripts\activate.bat"
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual.
    pause
    exit /b 1
)

:: Asegurar dependencias backend (channels, etc.)
echo Verificando dependencias del backend...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip no disponible en el entorno virtual
    pause
    exit /b 1
)
python -c "import channels" >nul 2>&1
if errorlevel 1 (
    echo Instalando dependencias del backend...
    echo Llamando al script de setup scripts\setup_backend_env.ps1 para crear el entorno e instalar dependencias.
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup_backend_env.ps1"
)

:: Iniciar backend con migraciones (SQL Server)
echo Iniciando backend en puerto 8000...
cd backend
:: Use the project's settings module (apps.core.settings). Many project entrypoints expect this module.
set "DJANGO_SETTINGS_MODULE=apps.core.settings"
python manage.py makemigrations
python manage.py migrate
start "Backend Django" cmd /k "python manage.py runserver 0.0.0.0:8000"
cd ..

:: Esperar a que el backend esté listo
echo Esperando a que el backend inicie...
timeout /t 5

:: Verificar dependencias del frontend
echo.
echo Verificando dependencias del frontend...
cd frontend
if not exist "node_modules" (
    echo Instalando dependencias del frontend...
    call npm install
)

:: Iniciar frontend
echo.
echo Iniciando frontend en puerto 3000...
start "Frontend Vite" cmd /k "npm run dev"
cd ..

:: Mostrar estado
echo.
echo ========================================
echo    SERVIDORES INICIADOS
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Para detener los servidores:
echo 1. Presiona Ctrl+C en cada ventana
echo 2. Escribe Y para confirmar
echo 3. Cierra las ventanas
echo.
echo Las ventanas de los servidores permanecerán abiertas para ver los logs
echo Presiona cualquier tecla para cerrar esta ventana...
pause >nul