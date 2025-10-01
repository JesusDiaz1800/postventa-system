@echo off
title Sistema de Postventa - Polifusion
color 0A

echo.
echo ========================================
echo    SISTEMA DE POSTVENTA - POLIFUSION
echo    Inicio Rapido y Optimizado
echo ========================================
echo.

echo [1/4] Verificando estructura del proyecto...
if not exist "backend\manage.py" (
    echo ERROR: No se encuentra el archivo manage.py
    pause
    exit /b 1
)
if not exist "frontend\package.json" (
    echo ERROR: No se encuentra el archivo package.json
    pause
    exit /b 1
)
echo ✓ Estructura del proyecto OK

echo.
echo [2/4] Verificando dependencias del backend...
cd backend
python -c "import django; print('Django:', django.get_version())" 2>nul
if errorlevel 1 (
    echo ERROR: Django no esta instalado
    echo Instalando dependencias...
    pip install -r requirements.txt
)
echo ✓ Backend OK

echo.
echo [3/4] Verificando dependencias del frontend...
cd ..\frontend
if not exist "node_modules" (
    echo Instalando dependencias del frontend...
    npm install
)
echo ✓ Frontend OK

echo.
echo [4/4] Iniciando servidores...
echo.
echo ========================================
echo    INICIANDO SISTEMA
echo ========================================
echo.

cd ..\backend
start "Backend Django" cmd /k "python manage.py runserver 0.0.0.0:8000"

cd ..\frontend
start "Frontend React" cmd /k "npm run dev"

echo.
echo ========================================
echo    SISTEMA INICIADO EXITOSAMENTE
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Presiona cualquier tecla para cerrar esta ventana...
pause >nul