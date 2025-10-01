@echo off
echo ========================================
echo GENERACIÓN DE CERTIFICADOS SSL
echo ========================================
echo.

REM Crear directorio SSL si no existe
if not exist "nginx\ssl" mkdir nginx\ssl

echo 🔐 Generando certificado SSL autofirmado...
echo.

REM Generar clave privada
openssl genrsa -out nginx\ssl\key.pem 2048

REM Generar certificado autofirmado
openssl req -new -x509 -key nginx\ssl\key.pem -out nginx\ssl\cert.pem -days 365 -subj "/C=MX/ST=Mexico/L=Mexico/O=Postventa/OU=IT/CN=192.168.1.161"

echo.
echo ✅ Certificados SSL generados exitosamente
echo.
echo 📁 Ubicación de los certificados:
echo    Clave privada: nginx\ssl\key.pem
echo    Certificado: nginx\ssl\cert.pem
echo.
echo ⚠️  NOTA: Estos son certificados autofirmados para desarrollo.
echo    Para producción, usa certificados de una CA confiable.
echo.
pause
