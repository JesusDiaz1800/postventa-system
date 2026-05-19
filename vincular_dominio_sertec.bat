@echo off
TITLE VINCULAR DOMINIO SERTEC SYSTEM
COLOR 0B

echo ========================================================
echo     VINCULANDO SERTEC.POLIFUSION.COM (SISTEMA SERTEC)
echo ========================================================
echo.

echo [1/3] Configurando redes de Cloudflare y Tunel...
python-portable\python\python.exe configurar_dominio_sertec.py

echo.
echo [2/3] Levantando la Aplicacion con PM2 (Modo Produccion)...
:: Intentar localizar PM2 en rutas comunes si no esta en el PATH
set PM2_PATH="C:\Users\jdiaz\AppData\Roaming\npm\pm2.cmd"
if not exist %PM2_PATH% set PM2_PATH=pm2

call %PM2_PATH% delete all >nul 2>&1
call %PM2_PATH% start ecosystem.config.js --update-env

echo.
echo [3/3] Guardando configuracion para el encendido automatico...
call %PM2_PATH% save

echo.
echo ========================================================
echo    TODO LISTO! El sistema ya esta en linea.
echo    Dominio: https://sertec.polifusion.com
echo ========================================================
echo.
pause
