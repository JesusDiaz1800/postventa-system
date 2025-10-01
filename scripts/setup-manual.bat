@echo off
echo ========================================
echo CONFIGURACION MANUAL DEL SISTEMA POSTVENTA
echo ========================================
echo.

REM Verificar Python
echo [1/8] Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado
    echo Instala Python 3.11+ desde https://python.org
    pause
    exit /b 1
)
echo Python OK
echo.

REM Verificar Node.js
echo [2/8] Verificando Node.js...
node --version
if %errorlevel% neq 0 (
    echo ERROR: Node.js no esta instalado
    echo Instala Node.js 18+ desde https://nodejs.org
    pause
    exit /b 1
)
echo Node.js OK
echo.

REM Crear entorno virtual Python
echo [3/8] Creando entorno virtual Python...
if not exist "venv" (
    python -m venv venv
    echo Entorno virtual creado
) else (
    echo Entorno virtual ya existe
)
echo.

REM Activar entorno virtual
echo [4/8] Activando entorno virtual...
call venv\Scripts\activate.bat
echo Entorno virtual activado
echo.

REM Instalar dependencias Python
echo [5/8] Instalando dependencias Python...
pip install --upgrade pip
pip install -r requirements.txt
echo Dependencias Python instaladas
echo.

REM Configurar base de datos
echo [6/8] Configurando base de datos...
python setup_database.py
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Error configurando base de datos
    echo Verifica que SQL Server este ejecutandose
)
echo.

REM Recopilar archivos estaticos
echo [7/8] Recopilando archivos estaticos...
python manage.py collectstatic --noinput
echo Archivos estaticos recopilados
echo.

REM Configurar frontend
echo [8/8] Configurando frontend...
cd ..\frontend
if not exist "node_modules" (
    npm install
    echo Dependencias frontend instaladas
) else (
    echo Dependencias frontend ya instaladas
)
cd ..\backend
echo.

echo ========================================
echo CONFIGURACION COMPLETADA
echo ========================================
echo.
echo Para iniciar el sistema:
echo.
echo 1. Backend (en esta ventana):
echo    call venv\Scripts\activate.bat
echo    python manage.py runserver
echo.
echo 2. Frontend (en otra ventana):
echo    cd frontend
echo    npm run dev
echo.
echo 3. Acceder a:
echo    - Frontend: http://localhost:3000
echo    - Backend: http://localhost:8000
echo    - Admin: http://localhost:8000/admin
echo.
echo Credenciales por defecto:
echo    Usuario: admin
echo    Contraseña: admin123
echo.
pause
