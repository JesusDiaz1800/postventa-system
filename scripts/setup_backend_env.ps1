<#
setup_backend_env.ps1
Robust backend environment setup for Windows
 - Creates/activates .venv using Python 3.13 (preferred)
 - Upgrades pip, setuptools, wheel
 - Installs python-dotenv first
 - Attempts to install requirements.txt and detects common native build issues
 - Provides remediation steps when native build tools are missing
#>

param(
    [string]$ProjectRoot = (Split-Path -Parent $MyInvocation.MyCommand.Definition),
    [string]$VenvName = '.venv'
)

Write-Host "[setup] Project root: $ProjectRoot"

$ErrorActionPreference = 'Stop'

$venvPath = Join-Path $ProjectRoot $VenvName
$backendPath = Join-Path $ProjectRoot 'backend'
$requirements = Join-Path $backendPath 'requirements.txt'

if (-not (Test-Path $backendPath)) { Write-Error "Backend path not found: $backendPath"; exit 1 }
if (-not (Test-Path $requirements)) { Write-Error "requirements.txt not found: $requirements"; exit 1 }

Write-Host "[setup] Ensuring Python virtual environment at: $venvPath"
try {
    # Prefer py -3.13 if present
    $hasPy = Get-Command py -ErrorAction SilentlyContinue
    if (-not (Test-Path (Join-Path $venvPath 'Scripts\activate.ps1'))) {
        if ($hasPy) {
            Write-Host "[setup] Creating venv with 'py -3.13'..."
            & py -3.13 -m venv $venvPath 2>$null
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "py -3.13 failed; falling back to system python -m venv"
                & python -m venv $venvPath
            }
        } else {
            Write-Host "[setup] Creating venv with system python..."
            & python -m venv $venvPath
        }
    }
} catch {
    Write-Error "Failed to create virtualenv: $_"; exit 1
}

# Activate the venv in this PowerShell session
$activate = Join-Path $venvPath 'Scripts\Activate.ps1'
if (-not (Test-Path $activate)) { Write-Error "Activation script not found: $activate"; exit 1 }
Write-Host "[setup] Activating venv..."
& $activate

Write-Host "[setup] Upgrading pip, setuptools, wheel..."
python -m pip install --upgrade pip setuptools wheel

Write-Host "[setup] Installing python-dotenv (required by settings)..."
python -m pip install python-dotenv

Write-Host "[setup] Installing backend requirements from $requirements..."
$logDir = Join-Path $ProjectRoot 'logs'
New-Item -ItemType Directory -Path $logDir -Force | Out-Null
$installLog = Join-Path $logDir 'pip_install_backend.log'

python -m pip install -r $requirements *>&1 | Tee-Object -FilePath $installLog

# Analyze log for known native build failures
$log = Get-Content $installLog -Raw
if ($log -match 'Microsoft Visual C\+\+ 14.0 or greater is required' -or $log -match 'error: Microsoft Visual C\+\+') {
    Write-Warning "Detected missing Microsoft Visual C++ Build Tools required to compile native extensions (pyodbc, Pillow, etc.)."
    Write-Host "Remedies (choose one):"
    Write-Host " 1) Install Microsoft C++ Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/"
    Write-Host " 2) Install the Windows 10/11 SDK from Visual Studio Installer."
    Write-Host " 3) Install Miniconda/Anaconda and use conda-forge for binary wheels (recommended to avoid builds)."
    Write-Host "After installing, re-run: .\start-system.bat"
    exit 2
}

if ($log -match 'error: subprocess-exited-with-error') {
    Write-Warning "pip reported subprocess-exited-with-error. Check $installLog for details."
    if ($log -match 'Building wheel for pyodbc') { Write-Host " - pyodbc build failed. Requires Microsoft C++ Build Tools and ODBC headers/drivers." }
    if ($log -match 'Getting requirements to build wheel did not run successfully' -and $log -match 'Pillow') { Write-Host " - Pillow build failed. Consider installing the binary wheel or Visual C++ Build Tools." }
    Write-Host "Consider using conda/miniconda to install pre-built wheels: https://docs.conda.io/en/latest/" 
    exit 3
}

Write-Host "[setup] Backend dependencies installed successfully (or no critical failures detected)."

# Run migrations (safe to fail if DB not configured)
Write-Host "[setup] Running migrations (may fail if DB not reachable)..."
Push-Location $backendPath
try {
    python manage.py makemigrations *>&1 | Tee-Object -FilePath (Join-Path $logDir 'makemigrations.log')
    python manage.py migrate *>&1 | Tee-Object -FilePath (Join-Path $logDir 'migrate.log')
} catch {
    Write-Warning "Migrations command failed; check logs in $logDir"
}
Pop-Location

Write-Host "[setup] Setup finished. Run start-system.bat to start servers." -ForegroundColor Green

