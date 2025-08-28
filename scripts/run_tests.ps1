# Cross-platform test runner (PowerShell)
# Usage: ./scripts/run_tests.ps1
$ErrorActionPreference = 'Stop'

function Log([string]$msg) { Write-Host "[tests] $msg" }
function Die([string]$msg) { Write-Error "[tests][ERR] $msg"; exit 1 }

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$TestFile = Join-Path $Root 'tests\test_use_cases.py'
if (!(Test-Path $TestFile)) { Die "Missing tests/test_use_cases.py" }

$Devlogs = Join-Path $Root '.devlogs'
New-Item -ItemType Directory -Force -Path $Devlogs | Out-Null

$Venv = Join-Path $Root '.venv\Scripts\Activate.ps1'
if (!(Test-Path $Venv)) {
  Log 'Creating Python venv at .venv ...'
  python -m venv .venv | Out-Null
}
. $Venv

python -m pip -q install -U pip | Out-Null
if (Test-Path (Join-Path $Root 'autobudget_backend\requirements.txt')) {
  pip -q install -r (Join-Path $Root 'autobudget_backend\requirements.txt') | Out-Null
}
pip -q install pytest | Out-Null

$env:PYTHONPATH = "$Root;" + ($env:PYTHONPATH)

Log 'Running pytest verbose run (logged to .devlogs\tests.log) ...'
$logPath = Join-Path $Devlogs 'tests.log'
$pytest = "python -m pytest -vv -rA `"$TestFile`""
cmd /c $pytest | Tee-Object -FilePath $logPath
$code = $LASTEXITCODE
Log ("Exit code: {0}" -f $code)

Log 'Tail of .devlogs\tests.log (last 80 lines):'
Get-Content $logPath -Tail 80

Log 'Emitting JUnit XML to .devlogs\pytest.xml ...'
$xmlPath = Join-Path $Devlogs 'pytest.xml'
cmd /c "python -m pytest -q --junitxml=`"$xmlPath`" `"$TestFile`"" | Out-Null

exit $code
