# Stop scripts

- Windows PowerShell

  - scripts/stop.ps1
  - Kills listeners on ports 8000 (backend), 3000 (frontend), and 5173 (Vite) by default.
  - Usage examples:
    - ./scripts/stop.ps1
    - ./scripts/stop.ps1 -Ports 8000,3000
    - ./scripts/stop.ps1 -WSL # also kill processes inside WSL for those ports

- WSL/Linux/macOS
  - scripts/stop.sh
  - Kills listeners on provided ports using fuser or lsof.
  - Usage examples:
    - bash scripts/stop.sh
    - bash scripts/stop.sh 8000 3000

## Notes

- These are safe best-effort stops; they target listening sockets only.
- If your dev servers use different ports, pass them in as shown above.
