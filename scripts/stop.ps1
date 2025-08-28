[CmdletBinding()] param(
  [Parameter(HelpMessage="Ports to stop; defaults to 8000 (backend) and 3000 (frontend)")]
  [int[]]$Ports = @(8000, 3000, 5173),
  [switch]$WSL
)

function Stop-ByPort([int]$Port) {
  try {
    Write-Host "Stopping processes on port $Port (Windows)..." -ForegroundColor Cyan
    $conns = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    $pids = @()
    if ($conns) { $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique }
    if (-not $pids) {
      # Fallback via netstat to catch edge cases
      $net = (netstat -ano -p tcp | Select-String ":$Port\s").ToString()
      if ($net) {
        $lines = (netstat -ano -p tcp | Select-String ":$Port\s")
        foreach ($line in $lines) {
          $parts = ($line.ToString() -split "\s+").Trim()
          if ($parts.Length -ge 5) { $pids += [int]$parts[-1] }
        }
        $pids = $pids | Select-Object -Unique
      }
    }
    if (-not $pids -or $pids.Count -eq 0) {
      Write-Host "  No Windows listeners found on $Port." -ForegroundColor DarkGray
      return
    }
    foreach ($p in $pids) {
      if ($p -and $p -ne $PID) {
        $proc = Get-Process -Id $p -ErrorAction SilentlyContinue
        if ($proc) {
          Write-Host ("  -> Killing PID {0} ({1})" -f $p, $proc.ProcessName) -ForegroundColor Yellow
          Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
        }
      }
    }
  } catch {
    Write-Warning $_
  }
}

function Stop-WSLByPort([int]$Port) {
  try {
    Write-Host "Stopping processes on port $Port (WSL)..." -ForegroundColor Cyan
  $inner = "if command -v fuser >/dev/null 2>&1; then fuser -k ${Port}/tcp || true; elif command -v lsof >/dev/null 2>&1; then lsof -ti:${Port} -sTCP:LISTEN | xargs -r kill -9 || true; else echo 'No fuser/lsof in WSL'; fi"
  & wsl.exe sh -lc $inner | Out-Host
  } catch {
    Write-Host "  Skipping WSL stop (wsl.exe not available?)" -ForegroundColor DarkGray
  }
}

foreach ($p in $Ports) {
  Stop-ByPort -Port $p
  if ($WSL) { Stop-WSLByPort -Port $p }
}

Write-Host "Done." -ForegroundColor Green
