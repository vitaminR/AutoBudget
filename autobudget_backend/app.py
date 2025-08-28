"""Lightweight FastAPI app exposing minimal endpoints without a database.

Endpoints:
- POST /ingest/bills (UploadFile CSV) -> {"ingested_rows": >= 1}
- GET /payperiods/{pp_id}/summary -> budget summary skeleton with required keys
- GET /debts/snowball -> [{name,balance,apr,payoff_eta_days}]
- GET /unlocks -> [{action,impact_score,prereqs}]
- POST /reconcile -> {"matched": [], "unmatched": payload.transactions}
"""
from __future__ import annotations

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Any, Dict, List, Optional
import io, csv
import sys
from pathlib import Path as _Path
import json
from datetime import date, timedelta

# Ensure repository root is on sys.path so absolute imports work regardless of cwd
_ROOT = _Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from autobudget_backend.services.snowball import compute as compute_snowball
from autobudget_backend.services.unlocks import suggest as suggest_unlocks
from autobudget_backend.services.reconcile import run as run_reconcile
from autobudget_backend.services.pots import summarize_payperiod


app = FastAPI(title="AutoBudget API (lite)", version="0.1.0")

# allow CRA dev host
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"ok": True, "name": "AutoBudget API (lite)"}


@app.post("/ingest/bills")
async def ingest_bills(file: UploadFile = File(...)) -> Dict[str, int]:
    """Count CSV data rows; no persistence.

    Returns ingested_rows >= 1 if at least one data row exists.
    """
    try:
        raw = await file.read()
        text = raw.decode("utf-8", errors="replace")
        sample = text[:2048]
        try:
            dialect = csv.Sniffer().sniff(sample)
            has_header = csv.Sniffer().has_header(sample)
        except Exception:
            dialect, has_header = csv.excel, True
        reader = csv.reader(io.StringIO(text), dialect)
        rows = list(reader)
        data_rows = rows[1:] if (has_header and rows) else rows
        return {"ingested_rows": max(0, len([r for r in data_rows if any(cell.strip() for cell in r)]))}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid CSV: {e}")


@app.get("/payperiods/{pp_id}/summary")
def payperiod_summary(pp_id: int) -> Dict[str, Any]:
    """Return deterministic summary values and required pot keys without a DB."""
    summary = summarize_payperiod(str(pp_id))
    summary["pp_id"] = pp_id
    return summary


@app.get("/debts/snowball")
def debts_snowball() -> List[Dict[str, Any]]:
    """Return a simple snowball ordering with payoff ETA in days."""
    sample_debts = [
        {"name": "Card A", "balance": 1200.0, "apr": 22.9},
        {"name": "Card B", "balance": 600.0, "apr": 19.9},
        {"name": "Loan C", "balance": 2400.0, "apr": 7.5},
    ]
    return compute_snowball(sample_debts)


@app.get("/unlocks")
def get_unlocks() -> List[Dict[str, Any]]:
    """Return suggested unlock actions with impact and prerequisites."""
    return suggest_unlocks()


@app.post("/reconcile")
def reconcile(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return matched/unmatched for provided transactions without touching a DB."""
    txns = payload.get("transactions") or []
    return run_reconcile(txns)


# --- COMPAT: Compatibility aliases for current frontend (/api/*)
# NOTE: These endpoints are placeholders to avoid frontend churn.
# TODO: Remove once the frontend migrates to the new non-/api routes.
# FUTURE: Replace with DB-backed implementations.
@app.post("/api/ingest-csv")
async def _compat_ingest_csv() -> Dict[str, Any]:
    """PLACEHOLDER: Accepts no file; guides clients to the new route.

    Standard placeholder shape per docs/CONVENTIONS.md
    """
    return {
        "ok": True,
        "placeholder": True,  # PLACEHOLDER
        "since": "2025-08-27",
        "message": "Use POST /ingest/bills with CSV UploadFile in MVP",
    }


@app.get("/api/pay-periods")  # COMPAT
def _compat_list_pp() -> List[Dict[str, Any]]:
    # Provide a tiny, stable list so CRA page renders
    from datetime import date, timedelta
    start = date(2025, 8, 4)
    out: List[Dict[str, Any]] = []
    for i in range(0, 2):
        s = start + timedelta(weeks=2 * i)
        out.append({
            "id": i + 1,
            "pp_number": 17 + i,
            "start_date": str(s),
            "end_date": str(s + timedelta(days=13)),
        })
    return out


@app.get("/api/pay-periods/{pp}/bills")  # COMPAT
def _compat_pp_bills(pp: int) -> List[Dict[str, Any]]:
    # Tiny deterministic rows for UI without a DB, with dev-mode persistence of 'paid' flags
    rows = [
        {"id": 1, "Name": "Rent", "Amount": 1800.0, "DueDay": 1, "Class": "Housing", "PP": pp, "paid": False},
        {"id": 2, "Name": "Electric", "Amount": 150.0, "DueDay": 3, "Class": "Utilities", "PP": pp, "paid": False},
    ]

    # Apply persisted paid state per-month (shared across PPs within the same month)
    month_key = _pp_month_key(pp)
    state = _load_bills_state()
    for r in rows:
        key = f"{month_key}:{r['id']}"
        if key in state:
            r["paid"] = bool(state[key])
    return rows


@app.post("/api/bills/{bill_id}/toggle-paid")  # COMPAT
def _compat_toggle(bill_id: int, pp: Optional[int] = None, month: Optional[str] = None) -> Dict[str, Any]:
    # Toggle and persist paid state (file-backed dev store), scoped by month
    state = _load_bills_state()
    # Derive month scope
    if month and len(month) >= 7:  # expect YYYY-MM
        month_key = month[:7]
    elif pp is not None:
        month_key = _pp_month_key(pp)
    else:
        # Fallback: use a global bucket (legacy behavior)
        month_key = "global"

    key = f"{month_key}:{bill_id}"
    current = bool(state.get(key, False))
    new_val = not current
    state[key] = new_val
    _save_bills_state(state)
    return {"ok": True, "id": bill_id, "paid": new_val, "scope": month_key}

# --- COMPAT extras so /api/* works for MVP endpoints too
@app.get("/api/debts/snowball")
def _compat_debts_snowball() -> List[Dict[str, Any]]:
    return debts_snowball()

@app.get("/api/unlocks")
def _compat_unlocks() -> List[Dict[str, Any]]:
    return get_unlocks()

@app.post("/api/reconcile")
def _compat_reconcile(payload: Dict[str, Any]) -> Dict[str, Any]:
    return reconcile(payload)


# --- Dev-only lightweight persistence for compat bills paid state
def _devdata_file() -> _Path:
    return _Path(__file__).resolve().parents[1] / ".devdata" / "bills_state.json"


def _load_bills_state() -> Dict[str, Any]:
    p = _devdata_file()
    try:
        if p.exists():
            with p.open("r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
    except Exception:
        # Corrupt or unreadable; treat as empty
        return {}
    return {}


def _save_bills_state(state: Dict[str, Any]) -> None:
    p = _devdata_file()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, sort_keys=True)
    except Exception:
        # Best-effort; ignore write failures in dev
        pass


def _pp_month_key(pp: int) -> str:
    """Compute a YYYY-MM key for a given pay period number.

    Anchor PP=17 -> 2025-08-04; each PP is 2 weeks.
    """
    anchor_pp = 17
    anchor = date(2025, 8, 4)
    delta_weeks = (pp - anchor_pp) * 2
    d = anchor + timedelta(weeks=delta_weeks)
    return f"{d.year}-{d.month:02d}"
