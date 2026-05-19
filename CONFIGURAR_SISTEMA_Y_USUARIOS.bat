@echo off
title SERTEC SYSTEM - CONFIGURADOR MAESTRO
echo ========================================================
echo CONFIGURANDO BASES DE DATOS Y USUARIOS VIP (SERTEC)
echo ========================================================
echo.

set PYTHON_PATH=%~dp0python312\python.exe
set SCRIPT_PATH=%~dp0backend\scripts\setup_final.py

if exist "%PYTHON_PATH%" (
    echo [OK] Usando Python Portable detectado en %PYTHON_PATH%
    "%PYTHON_PATH%" "%SCRIPT_PATH%"
) else (
    echo [ERROR] No se encuentra el Python Portable en %PYTHON_PATH%
    echo Intentando con python global...
    python "%SCRIPT_PATH%"
)

echo.
echo Presiona cualquier tecla para finalizar...
pause > nul
