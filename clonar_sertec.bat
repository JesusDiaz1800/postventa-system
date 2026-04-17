@echo off
echo =======================================================
echo          CLONANDO SISTEMA POSTVENTA A SERTEC
echo =======================================================
echo.

SET ORIGIN=%~dp0
REM Quitar barra invertida final si la hay
IF %ORIGIN:~-1%==\ SET ORIGIN=%ORIGIN:~0,-1%
SET DESTINATION=%USERPROFILE%\Desktop\sertec-system

echo Origen: %ORIGIN%
echo Destino: %DESTINATION%
echo.

IF EXIST "%DESTINATION%" (
    echo ALERTA: La carpeta destino ya existe.
    echo Asegurate de que este limpia o borrala antes de continuar.
    pause
    goto :eof
)

echo Iniciando copia (Omitiendo los archivos generados por usuarios y reportes en media)...
echo Esto tomara solo unos segundos...

robocopy "%ORIGIN%" "%DESTINATION%" /MIR /XD node_modules venv .venv .git __pycache__ dist .gemini .agent scratch tmp "backend\media" "backend\logs" "frontend\dist" /XF *.log *.sqlite3 .env.local C:\Users\jdiaz\Desktop\postventa-system\empezar_cloudflare.bat C:\Users\jdiaz\Desktop\postventa-system\vincular_dominio.bat

echo.
echo NOTA: Copiando el archivo .env manual para que tengas las variables base...
copy "%ORIGIN%\backend\.env" "%DESTINATION%\backend\.env" >nul
copy "%ORIGIN%\CONTEXTO_SERTEC.md" "%DESTINATION%\CONTEXTO_SERTEC.md" >nul

echo.
echo =======================================================
echo                 CLONACION FINALIZADA
echo =======================================================
echo Ya puedes abrir "sertec-system" en tu editor de codigo
echo e iniciar un nuevo chat con la IA desde esa carpeta.
echo.
pause
