@echo off
set PROJECT_ROOT=C:\Users\jdiaz\Desktop\postventa-system
set PM2_CMD=C:\Users\jdiaz\AppData\Roaming\npm\pm2.cmd
set NODE_EXE=C:\Program Files\nodejs\node.exe

cd /d "%PROJECT_ROOT%"
echo [$(date)] Inciando servicios de Postventa (SYSTEM) >> "%PROJECT_ROOT%\logs\startup.log"

REM Asegurar que el daemon de PM2 suba e inicie el ecosystem
call "%PM2_CMD%" kill
call "%PM2_CMD%" start ecosystem.config.js --update-env >> "%PROJECT_ROOT%\logs\startup.log" 2>&1
call "%PM2_CMD%" save >> "%PROJECT_ROOT%\logs\startup.log" 2>&1

exit /b 0
