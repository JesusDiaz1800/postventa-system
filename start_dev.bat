@echo off
global echo off
echo ===============================================
echo   INICIANDO POSTVENTA SYSTEM (DEV MODE)
echo ===============================================

echo [1/2] Iniciando Backend (Django)...
start "Postventa Backend" cmd /k "cd backend && if exist venv\Scripts\activate (call venv\Scripts\activate) else (echo WARNING: venv not found, using global python) && python manage.py runserver"

echo [2/2] Iniciando Frontend (Vite)...
start "Postventa Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ===============================================
echo   Sistema iniciando en nuevas ventanas.
echo   Backend: http://localhost:8000
echo   Frontend: http://localhost:5173
echo ===============================================
pause
