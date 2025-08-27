# PowerShell wrapper to run the Python snapshot generator from the repository root
param(
    [string]$Python = "python3"
)

# Resolve the repository root as the parent of the scripts folder
$repoRoot = Resolve-Path (Join-Path -Path $PSScriptRoot -ChildPath "..")
Set-Location $repoRoot

$script = Join-Path -Path $PSScriptRoot -ChildPath "generate_snapshot.py"
if (-not (Test-Path $script)) {
    Write-Error "Generator script not found: $script"
    exit 1
}

Write-Host "Running snapshot generator from repo root: $repoRoot"
& $Python $script
