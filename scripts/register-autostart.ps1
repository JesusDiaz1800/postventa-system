Param(
    [string]$ProjectRoot,
    [switch]$IncludeFrontend
)

if (-not $ProjectRoot -or $ProjectRoot -eq '') {
    $ProjectRoot = (Split-Path -Parent $MyInvocation.MyCommand.Path) | Split-Path -Parent
}

Write-Host "=== Registrando autoarranque (Task Scheduler) ===" -ForegroundColor Cyan

$taskNameBackend = "PostventaSystem-Backend"
$taskActionBackend = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ProjectRoot\scripts\run-backend.ps1`""
$taskTrigger = New-ScheduledTaskTrigger -AtStartup

# Principals posibles
$systemPrincipal = New-ScheduledTaskPrincipal -UserId "NT AUTHORITY\SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$userPrincipal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest

# Función de registro con fallback
function Register-With-Fallback($taskName, $taskAction, $taskTrigger, $systemPrincipal, $userPrincipal) {
    try {
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
    } catch {}
    
    try {
        Register-ScheduledTask -TaskName $taskName -Action $taskAction -Trigger $taskTrigger -Principal $systemPrincipal -Settings (New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 0)) | Out-Null
        Write-Host "✔ Tarea programada $taskName registrada con SYSTEM" -ForegroundColor Green
    } catch {
        Write-Host "⚠️ No se pudo registrar $taskName con SYSTEM, intentando con el usuario actual..." -ForegroundColor Yellow
        Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
        Register-ScheduledTask -TaskName $taskName -Action $taskAction -Trigger $taskTrigger -Principal $userPrincipal -Settings (New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 0)) | Out-Null
        Write-Host "✔ Tarea programada $taskName registrada con el usuario actual" -ForegroundColor Green
    }
}

Register-With-Fallback -taskName $taskNameBackend -taskAction $taskActionBackend -taskTrigger $taskTrigger -systemPrincipal $systemPrincipal -userPrincipal $userPrincipal

if ($IncludeFrontend) {
    $taskNameFrontend = "PostventaSystem-FrontendPreview"
    $taskActionFrontend = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ProjectRoot\scripts\run-frontend-preview.ps1`""
    Register-With-Fallback -taskName $taskNameFrontend -taskAction $taskActionFrontend -taskTrigger $taskTrigger -systemPrincipal $systemPrincipal -userPrincipal $userPrincipal
}

Write-Host "Autoarranque registrado. El servicio iniciará al arrancar Windows." -ForegroundColor Cyan
Exit 0


