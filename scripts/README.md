# Scripts

## Snapshot (alias)

- Windows PowerShell

  - `scripts/gen.ps1`
  - Alias wrapper for `generate_snapshot.ps1` (which calls `generate_snapshot.py`).
  - Usage:
    - `./scripts/gen.ps1`
    - `./scripts/gen.ps1 -Python python` (force interpreter)

- WSL/Linux/macOS
  - `scripts/gen.sh`
  - Alias wrapper for `scripts/generate_snapshot.py`.
  - Usage:
    - `bash ./scripts/gen.sh`

---

## Stop scripts

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
