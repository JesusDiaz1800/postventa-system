echo Instaldando dependencias de IA (Python Portable)...
python-portable\python\python.exe -m pip install "google-generativeai>=0.7.2" python-dotenv

echo.
echo Verificando configuracion...
python-portable\python\python.exe backend/check_ai_config.py
pause
