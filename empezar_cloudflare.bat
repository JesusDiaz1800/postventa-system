@echo off
echo =======================================================
echo     INSTALADOR Y CONFIGURADOR DE CLOUDFLARE TUNNEL
echo =======================================================
echo.

IF NOT EXIST "cloudflared.exe" (
    echo [1/3] Descargando Cloudflare Tunnel...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"
    echo Descarga completada.
) ELSE (
    echo [1/3] Cloudflare ya esta descargado.
)

echo.
echo [2/3] Abriendo inicio de sesion (Login)...
echo NOTA: Copia el enlace que saldra abajo y pegalo en tu navegador.
echo Luego autoriza el dominio "sistemati.cl"
echo.
cloudflared.exe tunnel login

pause
