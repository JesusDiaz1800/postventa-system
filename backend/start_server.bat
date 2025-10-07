@echo off
cd /d "%~dp0"
call python -m pip install channels daphne
call python manage.py collectstatic --noinput
call python manage.py migrate
start daphne -b 0.0.0.0 -p 8000 postventa_system.asgi:application