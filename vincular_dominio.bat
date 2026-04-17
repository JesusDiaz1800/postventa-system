@echo off
echo =======================================================
echo     VINCULANDO INCIDENCIAS.SISTEMATI.CL (SOLO 1 VEZ)
echo =======================================================
echo.

echo [1/3] Configurando redes de Cloudflare...
python-portable\python\python.exe configurar_dominio.py

echo.
echo [2/3] Levantando la Aplicacion y el Tunel...
call "C:\Users\jdiaz\AppData\Roaming\npm\pm2.cmd" delete all >nul 2>&1
call "C:\Users\jdiaz\AppData\Roaming\npm\pm2.cmd" start ecosystem.config.js --update-env

echo.
echo [3/3] Guardando configuracion para el encendido automatico...
call "C:\Users\jdiaz\AppData\Roaming\npm\pm2.cmd" save

echo.
echo TODO LISTO! Ya nunca mas tendras que correr este archivo.
pause
