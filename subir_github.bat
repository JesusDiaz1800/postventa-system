@echo off
echo =======================================================
echo          GUARDANDO Y SUBIENDO CAMBIOS A GITHUB
echo =======================================================
echo.

echo [1/3] Preparando los archivos modificados...
git add .

echo.
echo [2/3] Creando registro de la version...
git commit -m "Estabilizacion de SAP (Permisos DB vs API), Mega-Contexto Sertec, y Tunnel de Cloudflare configurado"

echo.
echo [3/3] Subiendo los cambios a la nube...
git push

echo.
echo =======================================================
echo                PROCESO TERMINADO
echo =======================================================
pause
