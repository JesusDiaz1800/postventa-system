# Install Postventa Hidden Service
# Este script registra el monitor de servicios para que corra como SYSTEM (Invisible) al arrancar.

$BACKEND_DIR = "C:\Users\jdiaz\Desktop\postventa-system\backend"
$BAT_PATH = "$BACKEND_DIR\run_postventa_services.bat"
$TASK_NAME = "PostventaSystem_BackgroundService"

Write-Host "--- CONFIGURANDO EJECUCIÓN INVISIBLE (SEGUNDO PLANO) ---" -ForegroundColor Cyan

# 1. Crear la acción (Ejecutar el .bat)
$Action = New-ScheduledTaskAction -Execute $BAT_PATH -WorkingDirectory $BACKEND_DIR

# 2. Crear el disparador (Al arrancar el equipo)
$Trigger = New-ScheduledTaskTrigger -AtStartup

# 3. Configurar ajustes (No detener por batería, permitir ejecución inmediata)
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Days 365)

# 4. Registrar la tarea como SYSTEM (Invisible y Permanente)
# Nota: Esto requiere que PowerShell se ejecute como Administrador.

try {
    # Eliminar si ya existe una con el mismo nombre para evitar duplicados
    Unregister-ScheduledTask -TaskName $TASK_NAME -Confirm:$false -ErrorAction SilentlyContinue

    Register-ScheduledTask -TaskName $TASK_NAME `
                           -Action $Action `
                           -Trigger $Trigger `
                           -Settings $Settings `
                           -User "SYSTEM" `
                           -RunLevel Highest

    Write-Host "`n[EXITO] El sistema se ha registrado para correr en SEGUNDO PLANO (Invisible)." -ForegroundColor Green
    Write-Host "A partir de ahora, el proyecto subirá solo al encender el PC y nadie podrá cerrarlo por error." -ForegroundColor Green
    Write-Host "`nPara iniciar el servicio AHORA mismo sin reiniciar el PC, puedes correr:" -ForegroundColor Yellow
    Write-Host "Start-ScheduledTask -TaskName '$TASK_NAME'" -ForegroundColor Yellow
}
catch {
    Write-Host "`n[ERROR] No se pudo registrar la tarea. ¿Aseguraste ejecutar PowerShell como Administrador?" -ForegroundColor Red
}
