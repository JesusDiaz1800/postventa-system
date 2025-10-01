@echo off
echo ========================================
echo    VERIFICACION DEL SISTEMA
echo ========================================
echo.

echo [1/6] Verificando estructura de archivos...
if not exist "backend\manage.py" (
    echo ERROR: manage.py no encontrado
    goto :error
)
if not exist "frontend\package.json" (
    echo ERROR: package.json no encontrado
    goto :error
)
echo ✓ Estructura de archivos OK

echo [2/6] Verificando dependencias del backend...
cd backend
python -c "import django; print('Django:', django.get_version())" 2>nul || (
    echo ERROR: Django no instalado
    goto :error
)
echo ✓ Django instalado

echo [3/6] Verificando base de datos...
python manage.py check --database default 2>nul || (
    echo ERROR: Problema con la base de datos
    goto :error
)
echo ✓ Base de datos OK

echo [4/6] Verificando migraciones...
python manage.py showmigrations --plan | findstr "[ ]" >nul && (
    echo ADVERTENCIA: Hay migraciones pendientes
    echo Aplicando migraciones...
    python manage.py migrate
) || echo ✓ Migraciones OK

echo [5/6] Verificando dependencias del frontend...
cd ..\frontend
npm list --depth=0 2>nul || (
    echo ERROR: Dependencias del frontend no instaladas
    goto :error
)
echo ✓ Dependencias del frontend OK

echo [6/6] Verificando configuración...
if exist "backend\.env" (
    echo ✓ Archivo .env encontrado
) else (
    echo ADVERTENCIA: Archivo .env no encontrado, usando configuración por defecto
)

echo.
echo ========================================
echo    SISTEMA VERIFICADO EXITOSAMENTE
echo ========================================
echo.
echo El sistema está listo para usar.
echo Ejecuta 'start-system.bat' para iniciar los servidores.
echo.
goto :end

:error
echo.
echo ========================================
echo    ERROR EN LA VERIFICACION
echo ========================================
echo.
echo Por favor, revisa los errores anteriores y corrige los problemas.
echo.

:end
pause
