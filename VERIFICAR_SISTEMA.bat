@echo off
title Verificacion del Sistema PostVenta
color 0B

echo.
echo ========================================
echo   VERIFICACION DEL SISTEMA POSTVENTA
echo ========================================
echo.

echo [1/3] Verificando Backend Django...
python-portable\python\python.exe -c "import requests; r = requests.get('http://192.168.1.234:8000/', timeout=5); print('Backend Status:', r.status_code)" 2>nul
if errorlevel 1 (
    echo ERROR: Backend no disponible
) else (
    echo OK: Backend funcionando
)

echo.
echo [2/3] Verificando Frontend React...
python-portable\python\python.exe -c "import requests; r = requests.get('http://192.168.1.234:5173/', timeout=5); print('Frontend Status:', r.status_code)" 2>nul
if errorlevel 1 (
    echo ERROR: Frontend no disponible
) else (
    echo OK: Frontend funcionando
)

echo.
echo [3/3] Verificando Autenticacion...
python-portable\python\python.exe -c "import requests; r = requests.post('http://192.168.1.234:8000/api/auth/login/', json={'username': 'jdiaz', 'password': 'adminJDR'}, timeout=5); print('Login Status:', r.status_code)" 2>nul
if errorlevel 1 (
    echo ERROR: Autenticacion no disponible
) else (
    echo OK: Autenticacion funcionando
)

echo.
echo ========================================
echo   VERIFICACION COMPLETADA
echo ========================================
echo.
echo Para verificar completamente:
echo   python-portable\python\python.exe test-sql-connection.py
echo.
pause
