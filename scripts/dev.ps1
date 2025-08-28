<#
 Hybrid Windows dev script
 - If WSL is available, delegates to scripts/dev.sh in WSL (Linux-like env).
 - Otherwise, runs a native PowerShell dev runner: sets up venv, installs deps (filters uvloop),
   starts FastAPI via uvicorn with reload, optional frontend via npm, writes logs, waits on health,
   and cleans up child processes on exit.
#>
$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $RepoRoot 'autobudget_backend'
$FrontendDir = Join-Path $RepoRoot 'autobudget_frontend'
$DevLogs = Join-Path $RepoRoot '.devlogs'
$BackendHealth = 'http://127.0.0.1:8000/openapi.json'
$FrontendHealth = 'http://127.0.0.1:3000'

# Backend module selection (default MVP). Override with USE_DB=1 or BACKEND=legacy|db or explicit BACKEND_MODULE
$BackendModule = if ($env:BACKEND_MODULE) { $env:BACKEND_MODULE } else { 'autobudget_backend.app:app' }
if ($env:USE_DB -eq '1' -or $env:BACKEND -eq 'legacy' -or $env:BACKEND -eq 'db') {
  $BackendModule = 'autobudget_backend.main:app'
}

function Write-Log([string]$msg) { Write-Host "[dev] $msg" }
function Die([string]$msg) { Write-Error $msg; exit 1 }

# 1) Try to use WSL if available
try {
  $WSLPath = & wsl wslpath -a "$RepoRoot" 2>$null
} catch { $WSLPath = $null }
if ($null -ne $WSLPath -and -not [string]::IsNullOrWhiteSpace($WSLPath)) {
  $envPart = ''
  if ($env:DEV_SEED) { $envPart = 'DEV_SEED=1 ' }
  Write-Log "WSL detected; delegating to scripts/dev.sh ..."
  & wsl bash -lc "cd '$WSLPath'; ${envPart}bash scripts/dev.sh"
  exit $LASTEXITCODE
}

# 2) Native PowerShell fallback
Write-Log "WSL not available; starting Windows-native dev runner ..."

function Require($name) {
  if (-not (Get-Command $name -ErrorAction SilentlyContinue)) {
    Die "Missing dependency: $name"
  }
}

function Wait-Http($url, [int]$tries = 120, [int]$delayMs = 500) {
  for ($i = 0; $i -lt $tries; $i++) {
    try {
      $resp = Invoke-WebRequest -Uri $url -TimeoutSec 2 -UseBasicParsing
      if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 500) { return $true }
    } catch {
      # ignore
    }
    Start-Sleep -Milliseconds $delayMs
  }
  return $false
}

function Ensure-Venv([string]$backendDir) {
  $venvPath = Join-Path $backendDir '.venv'
  $venvPython = Join-Path $venvPath 'Scripts\python.exe'
  if (-not (Test-Path $venvPython)) {
    Write-Log "Creating Python venv ..."
    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
      & $pyLauncher.Source -3 -m venv $venvPath
    } else {
      $py = Get-Command python -ErrorAction SilentlyContinue
      if (-not $py) { Die 'Python not found. Install Python 3.x and ensure it is on PATH.' }
      & $py.Source -m venv $venvPath
    }
  }
  return $venvPython
}

function Install-Requirements([string]$venvPython, [string]$backendDir) {
  & $venvPython -m pip install -q --upgrade pip
  $req = Join-Path $backendDir 'requirements.txt'
  if (Test-Path $req) {
    # Filter out Linux-only packages like uvloop for Windows installs
    $tempReq = Join-Path $env:TEMP 'requirements.win.txt'
    (Get-Content $req) | Where-Object { $_ -notmatch '^\s*uvloop\b' } | Set-Content -Path $tempReq -NoNewline:$false
    Write-Log "Installing Python dependencies (Windows-safe) ..."
    & $venvPython -m pip install -q -r $tempReq
  }
}

function Start-Backend() {
  if (-not (Test-Path $BackendDir)) { Die "Backend directory not found: $BackendDir" }
  $venvPython = Ensure-Venv $BackendDir
  Install-Requirements $venvPython $BackendDir

  if ($env:DEV_SEED) {
    Write-Log "Seeding (DEV_SEED=1) ..."
    try {
      & $venvPython (Join-Path $RepoRoot 'scripts\ingest_data.py')
    } catch {
      Write-Log "Seed failed (continuing)"
    }
  }

  if (-not (Test-Path $DevLogs)) { New-Item -ItemType Directory -Path $DevLogs | Out-Null }
  $log = Join-Path $DevLogs 'backend.log'
  $pidfile = Join-Path $DevLogs 'backend.pid'

  # Ensure PYTHONPATH contains repo root for absolute imports
  $currentPyPath = $env:PYTHONPATH
  if ([string]::IsNullOrWhiteSpace($currentPyPath)) { $env:PYTHONPATH = $RepoRoot } else { $env:PYTHONPATH = "$RepoRoot;$currentPyPath" }

  $args = @('-m','uvicorn', $BackendModule,'--host','127.0.0.1','--port','8000','--reload','--reload-dir', $BackendDir)
  Write-Log "Starting backend (uvicorn $BackendModule) ..."
  $p = Start-Process -FilePath $venvPython -ArgumentList $args -WorkingDirectory $RepoRoot -NoNewWindow -RedirectStandardOutput $log -RedirectStandardError $log -PassThru
  Set-Content -Path $pidfile -Value $p.Id

  Write-Log "Backend PID $($p.Id); waiting for $BackendHealth ..."
  if (-not (Wait-Http $BackendHealth 120 500)) {
    Write-Log "Backend logs (tail):"
    if (Test-Path $log) { Get-Content $log -Tail 120 }
    Die "Backend did not become ready"
  }
  Write-Log "Backend is ready."
  return $p
}

function Start-Frontend() {
  if (-not (Test-Path $FrontendDir)) { Write-Log "Frontend directory not found ($FrontendDir); skipping frontend."; return $null }
  if (-not (Get-Command npm -ErrorAction SilentlyContinue)) { Write-Log 'npm not found; skipping frontend.'; return $null }

  if (-not (Test-Path $DevLogs)) { New-Item -ItemType Directory -Path $DevLogs | Out-Null }
  $log = Join-Path $DevLogs 'frontend.log'
  $pidfile = Join-Path $DevLogs 'frontend.pid'

  Write-Log "Starting frontend (npm start) ..."
  $prevPort = $env:PORT
  $env:PORT = '3000'
  $p = Start-Process -FilePath 'npm' -ArgumentList @('start') -WorkingDirectory $FrontendDir -NoNewWindow -RedirectStandardOutput $log -RedirectStandardError $log -PassThru
  if ($null -ne $prevPort) { $env:PORT = $prevPort } else { Remove-Item Env:PORT -ErrorAction SilentlyContinue }
  Set-Content -Path $pidfile -Value $p.Id

  Write-Log "Frontend PID $($p.Id); waiting for $FrontendHealth ..."
  if (-not (Wait-Http $FrontendHealth 120 500)) {
    Write-Log "Frontend logs (tail):"
    if (Test-Path $log) { Get-Content $log -Tail 120 }
    Die "Frontend did not become ready"
  }
  Write-Log "Frontend is ready."
  return $p
}

# Pre-flight checks (only for tools we actually use here)
Require Invoke-WebRequest

$backendProc = $null
$frontendProc = $null
try {
  $backendProc = Start-Backend
  $frontendProc = Start-Frontend

  Write-Log @"
All services up:
- Backend:  http://127.0.0.1:8000
- Frontend: http://127.0.0.1:3000

Logs: .devlogs/{backend.log,frontend.log}
Press Ctrl+C to stop.
"@

  $waitIds = @()
  if ($backendProc) { $waitIds += $backendProc.Id }
  if ($frontendProc) { $waitIds += $frontendProc.Id }
  if ($waitIds.Count -gt 0) { Wait-Process -Id $waitIds }
}
finally {
  Write-Log 'Stopping services ...'
  foreach ($p in @($frontendProc, $backendProc)) {
    if ($p -and -not $p.HasExited) {
      try { Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue } catch {}
    }
  }
  Write-Log 'Done.'
}
