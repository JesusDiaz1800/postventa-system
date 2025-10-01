@echo off
echo ========================================
echo    DEPLOYMENT EMPRESARIAL - POSTVENTA
echo ========================================
echo.

REM Verificar si se ejecuta como administrador
net session >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Ejecutando como administrador
) else (
    echo [ERROR] Este script debe ejecutarse como administrador
    pause
    exit /b 1
)

echo.
echo [1/8] Verificando dependencias...
python --version >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Python instalado
) else (
    echo [ERROR] Python no encontrado. Instalando...
    winget install Python.Python.3.11
)

node --version >nul 2>&1
if %errorLevel% == 0 (
    echo [OK] Node.js instalado
) else (
    echo [ERROR] Node.js no encontrado. Instalando...
    winget install OpenJS.NodeJS
)

echo.
echo [2/8] Creando estructura de carpetas...
if not exist "C:\Documentos" mkdir "C:\Documentos"
if not exist "C:\Documentos\visit_report" mkdir "C:\Documentos\visit_report"
if not exist "C:\Documentos\lab_report" mkdir "C:\Documentos\lab_report"
if not exist "C:\Documentos\supplier_report" mkdir "C:\Documentos\supplier_report"
if not exist "C:\Documentos\quality_report" mkdir "C:\Documentos\quality_report"
echo [OK] Carpetas creadas

echo.
echo [3/8] Configurando permisos de carpeta...
icacls "C:\Documentos" /grant "Todos:(OI)(CI)F" /T
icacls "C:\Documentos" /grant "Usuarios:(OI)(CI)F" /T
echo [OK] Permisos configurados

echo.
echo [4/8] Instalando dependencias Python...
cd backend
pip install -r requirements.txt
if %errorLevel% == 0 (
    echo [OK] Dependencias Python instaladas
) else (
    echo [ERROR] Error instalando dependencias Python
    pause
    exit /b 1
)

echo.
echo [5/8] Configurando base de datos...
python manage.py makemigrations
python manage.py migrate
if %errorLevel% == 0 (
    echo [OK] Base de datos configurada
) else (
    echo [ERROR] Error configurando base de datos
    pause
    exit /b 1
)

echo.
echo [6/8] Creando superusuario...
python manage.py createsuperuser --noinput --username admin --email admin@empresa.com
if %errorLevel% == 0 (
    echo [OK] Superusuario creado (admin/admin123)
) else (
    echo [WARNING] Error creando superusuario (puede que ya exista)
)

echo.
echo [7/8] Instalando dependencias Frontend...
cd ..\frontend
npm install
if %errorLevel% == 0 (
    echo [OK] Dependencias Frontend instaladas
) else (
    echo [ERROR] Error instalando dependencias Frontend
    pause
    exit /b 1
)

echo.
echo [8/8] Configurando servicio Windows...
cd ..
echo [INFO] Creando servicio Windows para el backend...
sc create "PostventaBackend" binPath="C:\Python311\python.exe C:\ruta\a\tu\proyecto\backend\manage.py runserver 0.0.0.0:8000" start=auto
if %errorLevel% == 0 (
    echo [OK] Servicio backend creado
) else (
    echo [WARNING] Error creando servicio (puede que ya exista)
)

echo.
echo ========================================
echo    DEPLOYMENT COMPLETADO
echo ========================================
echo.
echo [INFO] Configuración empresarial:
echo   - Documentos: C:\Documentos\
echo   - Base de datos: SQL Server
echo   - Usuario admin: admin / admin123
echo   - URL: http://localhost:8000
echo.
echo [INFO] Para configurar carpeta compartida:
echo   1. Compartir carpeta C:\Documentos
echo   2. Configurar SHARED_DOCUMENTS_PATH en settings-empresa.py
echo   3. Reiniciar servicios
echo.
echo [INFO] Para acceso remoto:
echo   1. Configurar IIS
echo   2. Configurar dominio
echo   3. Configurar SSL
echo.
pause
