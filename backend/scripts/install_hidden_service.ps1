# Postventa System - Registro de Servicio de Sistema (Autoinicio Permanente)
# NOTA: Este script DEBE ejecutarse como ADMINISTRADOR por personal de TI.

$PROJECT_ROOT = "C:\Users\jdiaz\Desktop\postventa-system"
$STARTUP_BAT = "$PROJECT_ROOT\backend\scripts\start_pm2_startup.bat"
$TASK_NAME = "PostventaSystem_Daemon_Autostart"

Write-Host "`n--- POSTVENTA SYSTEM: INSTALADOR DE SERVICIO ---" -ForegroundColor Cyan

# 1. Validar permisos de administrador
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "`n[ERROR] DEBE EJECUTAR ESTA CONSOLA COMO ADMINISTRADOR." -ForegroundColor Red
    Write-Host "Por favor, cierre y vuelva a abrir PowerShell (Clic derecho -> Ejecutar como administrador)."
    exit
}

# 2. Registrar la Tarea Programada (SYSTEM)
Write-Host "[*] Registrando tarea programada: $TASK_NAME" -ForegroundColor Yellow

$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$STARTUP_BAT`"" -WorkingDirectory $PROJECT_ROOT
$Trigger = New-ScheduledTaskTrigger -AtStartup
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Days 365)

try {
    # Limpiar instalaciones previas
    Unregister-ScheduledTask -TaskName $TASK_NAME -Confirm:$false -ErrorAction SilentlyContinue

    Register-ScheduledTask -TaskName $TASK_NAME `
                           -Action $Action `
                           -Trigger $Trigger `
                           -Settings $Settings `
                           -User "SYSTEM" `
                           -RunLevel Highest

    Write-Host "`n[EXITO] El sistema se ha registrado como Servicio de Sistema." -ForegroundColor Green
    Write-Host "La aplicacion se iniciara SOLA en cada arranque del servidor, sin necesidad de login." -ForegroundColor Green
    Write-Host "`nPara iniciar el servicio inmediatamente sin reiniciar:" -ForegroundColor Yellow
    Write-Host ">>> Start-ScheduledTask -TaskName '$TASK_NAME'" -ForegroundColor Cyan
}
catch {
    Write-Host "`n[ERROR CRITICO] No se pudo registrar la tarea." -ForegroundColor Red
    Write-Host $_.Exception.Message
}
