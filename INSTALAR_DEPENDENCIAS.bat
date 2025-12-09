@echo off
title Instalacion de Dependencias - PostVenta
color 0E

echo.
echo ========================================
echo   INSTALACION DE DEPENDENCIAS
echo ========================================
echo.

echo [1/4] Verificando Python Portable...
if not exist "python-portable\python\python.exe" (
    echo ERROR: Python portable no encontrado
    echo Descargue e instale Python portable en la carpeta python-portable
    pause
    exit /b 1
) else (
    echo OK: Python portable encontrado
)

echo.
echo [2/4] Verificando dependencias Python...
cd backend
python-portable\python\python.exe -c "import django; print('Django:', django.get_version())" 2>nul
if errorlevel 1 (
    echo ERROR: Django no instalado
    echo Instalando dependencias Python...
    ..\python-portable\python\python.exe -m pip install -r requirements.txt
) else (
    echo OK: Django instalado
)
cd ..

echo.
echo [3/4] Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js no encontrado
    echo Instale Node.js desde https://nodejs.org
    pause
    exit /b 1
) else (
    echo OK: Node.js encontrado
)

echo.
echo [4/4] Verificando dependencias Frontend...
cd frontend
if not exist "node_modules" (
    echo Instalando dependencias Frontend...
    npm install
    if errorlevel 1 (
        echo ERROR: Fallo en la instalacion de dependencias Frontend
        cd ..
        pause
        exit /b 1
    )
) else (
    echo OK: Dependencias Frontend encontradas
)
cd ..

echo.
echo ========================================
echo   DEPENDENCIAS VERIFICADAS
echo ========================================
echo.
echo Sistema listo para iniciar:
echo   INICIAR_SISTEMA_PRODUCCION.bat
echo.
pause
