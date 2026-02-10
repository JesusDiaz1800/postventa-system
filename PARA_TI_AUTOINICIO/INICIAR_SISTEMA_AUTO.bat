@echo off
:: INICIAR_SISTEMA_AUTO.bat
:: Script optimizado para arranque automatico ("Headless")
:: Polifusion S.A.

:: Directorio raiz del proyecto (asumiendo ubicacion fija en Desktop\postventa-system)
:: AJUSTAR ESTA RUTA SI SE MUEVE LA CARPETA
set "PROJECT_ROOT=C:\Users\jdiaz\Desktop\postventa-system"

cd /d "%PROJECT_ROOT%"

:: Crear carpeta de logs si no existe
if not exist "logs" mkdir logs

:: 1. Iniciar Backend (Invisible usando pythonw)
:: pythonw.exe ejecuta scripts sin ventana de consola
echo [%DATE% %TIME%] Iniciando Backend... >> logs\autostart.log
start "" "python-portable\python\pythonw.exe" -m daphne -b 0.0.0.0 -p 8000 postventa_system.asgi:application

:: Esperar un momento a que el backend respire
timeout /t 5 /nobreak >nul

:: 2. Iniciar Frontend (Invisible usando script VBS)
echo [%DATE% %TIME%] Iniciando Frontend... >> logs\autostart.log
cd frontend
:: Usamos run_hidden.vbs para lanzar npm run dev sin ventana
:: Asegúrese de que run_hidden.vbs esté en la carpeta PARA_TI_AUTOINICIO o ruta conocida
:: Aquí asumimos que llamamos npm directamente, pero para ocultarlo necesitamos el VBS.
:: Alternativa robusta: Ejecutar npm y minizar, o usar VBS wrapper.
wscript "%PROJECT_ROOT%\PARA_TI_AUTOINICIO\run_hidden.vbs" npm run dev -- --host 0.0.0.0

echo [%DATE% %TIME%] Sistema Iniciado. >> logs\autostart.log
exit
