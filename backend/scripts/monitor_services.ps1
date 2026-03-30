# Monitor de Servicios Postventa (Windows)
# Este script asegura que Daphne y Celery estén siempre corriendo.

$BACKEND_DIR = "$PSScriptRoot\.."
$PYTHON_EXE = "$BACKEND_DIR\..\python312\python.exe"

function Start-Daphne {
    Write-Host "[$(Get-Date)] Iniciando Daphne (ASGI)..." -ForegroundColor Cyan
    Start-Process -FilePath $PYTHON_EXE -ArgumentList "-m daphne -b 0.0.0.0 -p 8000 apps.core.asgi:application" -WorkingDirectory $BACKEND_DIR -WindowStyle Minimized
}

function Start-Worker {
    Write-Host "[$(Get-Date)] Iniciando Celery Worker..." -ForegroundColor Green
    Start-Process -FilePath $PYTHON_EXE -ArgumentList "-m celery -A apps.core worker --loglevel=info --pool=threads" -WorkingDirectory $BACKEND_DIR -WindowStyle Minimized
}

function Start-Worker-Beat {
    Write-Host "[$(Get-Date)] Iniciando Celery Beat..." -ForegroundColor Yellow
    Start-Process -FilePath $PYTHON_EXE -ArgumentList "-m celery -A apps.core beat --loglevel=info" -WorkingDirectory $BACKEND_DIR -WindowStyle Minimized
}

while ($true) {
    # Verificar Daphne (Puerto 8000)
    $daphneRunning = Get-Process | Where-Object { $_.ProcessName -eq "daphne" }
    if (-not $daphneRunning) {
        Start-Daphne
    }

    # Verificar Celery Worker
    $celeryProcessing = Get-Process | Where-Object { $_.CommandLine -like "*worker*" }
    if (-not $celeryProcessing) {
        Start-Worker
    }

    # Verificar Celery Beat
    $beatRunning = Get-Process | Where-Object { $_.CommandLine -like "*beat*" }
    if (-not $beatRunning) {
        Start-Worker-Beat
    }

    Write-Host "[$(Get-Date)] Servicios monitoreados. Durmiendo 60s..."
    Start-Sleep -Seconds 60
}
