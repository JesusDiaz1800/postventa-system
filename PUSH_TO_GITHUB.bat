@echo off
echo =======================================================
echo          SUBIENDO CAMBIOS DE SERTEC A GITHUB
echo =======================================================
echo.

REM 1. Verificar si git esta inicializado
if not exist .git (
    echo [1/4] Inicializando repositorio Git...
    git init
    git remote add origin https://github.com/JesusDiaz1800/postventa-system.git
    git branch -M main
) else (
    echo [1/4] Repositorio Git ya inicializado.
)

echo.
echo [2/4] Preparando los archivos modificados...
git add .

echo.
echo [3/4] Creando registro de la version...
set /p msg="Mensaje del commit (Enter para default): "
if "%msg%"=="" set msg="Estabilizacion Visit Report 2.0: Solucion Error 500 y Fotos antes de guardar"
git commit -m %msg%

echo.
echo [4/4] Subiendo los cambios a la nube...
echo Intentando hacer push a origin main...
git push -u origin main

echo.
echo =======================================================
echo                PROCESO TERMINADO
echo =======================================================
pause
