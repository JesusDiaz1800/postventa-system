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
# Intentar crear tarea como SYSTEM; si no hay permisos, crearla para el usuario actual
$canUseSystem = $true
try {
    $null = New-ScheduledTaskPrincipal -UserId "NT AUTHORITY\SYSTEM" -LogonType ServiceAccount -RunLevel Highest
} catch { $canUseSystem = $false }

if ($canUseSystem) {
    $taskPrincipal = New-ScheduledTaskPrincipal -UserId "NT AUTHORITY\SYSTEM" -LogonType ServiceAccount -RunLevel Highest
} else {
    $currentUser = "$env:USERDOMAIN\$env:USERNAME"
    $taskPrincipal = New-ScheduledTaskPrincipal -UserId $currentUser -LogonType Interactive -RunLevel Highest
}

try {
    Unregister-ScheduledTask -TaskName $taskNameBackend -Confirm:$false -ErrorAction SilentlyContinue
} catch {}
Register-ScheduledTask -TaskName $taskNameBackend -Action $taskActionBackend -Trigger $taskTrigger -Principal $taskPrincipal -Settings (New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 0)) | Out-Null
Write-Host "✔ Tarea programada Backend registrada: $taskNameBackend" -ForegroundColor Green

if ($IncludeFrontend) {
    $taskNameFrontend = "PostventaSystem-FrontendPreview"
    $taskActionFrontend = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ProjectRoot\scripts\run-frontend-preview.ps1`""
    try { Unregister-ScheduledTask -TaskName $taskNameFrontend -Confirm:$false -ErrorAction SilentlyContinue } catch {}
    Register-ScheduledTask -TaskName $taskNameFrontend -Action $taskActionFrontend -Trigger $taskTrigger -Principal $taskPrincipal -Settings (New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -ExecutionTimeLimit (New-TimeSpan -Minutes 0)) | Out-Null
    Write-Host "✔ Tarea programada Frontend registrada: $taskNameFrontend" -ForegroundColor Green
}

Write-Host "Autoarranque registrado. El servicio iniciará al arrancar Windows." -ForegroundColor Cyan
Exit 0


