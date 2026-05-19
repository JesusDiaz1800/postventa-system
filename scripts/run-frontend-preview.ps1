Param(
    [string]$ProjectRoot
)

if (-not $ProjectRoot -or $ProjectRoot -eq '') {
    $ProjectRoot = (Split-Path -Parent $MyInvocation.MyCommand.Path) | Split-Path -Parent
}

Set-Location (Join-Path $ProjectRoot "frontend")

Start-Process -FilePath "npm" -ArgumentList "run preview -- --host 0.0.0.0 --port 3000" -NoNewWindow
Exit 0


