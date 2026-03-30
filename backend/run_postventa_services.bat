@echo off
TITLE Postventa System - Service Monitor
echo Iniciando Monitor de Servicios Postventa...
powershell -ExecutionPolicy Bypass -File "%~dp0scripts\monitor_services.ps1"
pause
