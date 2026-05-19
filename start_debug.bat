@echo off
echo ===================================================
echo   INICIANDO SISTEMA DE POSTVENTA - MODO DEBUG
echo ===================================================
echo.
echo [1/4] Deteniendo procesos anteriores...
taskkill /F /IM node.exe >nul 2>&1
taskkill /F /IM python.exe >nul 2>&1
echo Procesos detenidos.
echo.

echo [2/4] Buscando ejecutable de Python...
set PYTHON_CMD=python

if exist "python-portable\python\python.exe" (
    echo Python Portable detectado.
    set PYTHON_CMD=..\python-portable\python\python.exe
) else (
    if exist "python312\python.exe" (
        echo Python 3.12 local detectado.
        set PYTHON_CMD=..\python312\python.exe
    ) else (
        echo Usando Python global del sistema.
    )
)

echo [3/4] Iniciando Backend (Django)...
start "BACKEND - DJANGO" cmd /k "cd backend && %PYTHON_CMD% manage.py runserver 0.0.0.0:8000"
echo Backend iniciado en nueva ventana.
echo.

echo [4/4] Iniciando Frontend (Vite)...
start "FRONTEND - VITE" cmd /k "cd frontend && npm run dev -- --force"
echo Frontend iniciado en nueva ventana.
echo.

echo ===================================================
echo   SISTEMA INICIANDO...
echo   Backend: http://localhost:8000
echo   Frontend: http://localhost:5173
echo.
echo   Revise las ventanas para ver errores.
echo ===================================================
pause
