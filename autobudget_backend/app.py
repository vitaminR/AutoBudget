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
from typing import Any, Dict, List
import io, csv

from .services.snowball import compute as compute_snowball
from .services.unlocks import suggest as suggest_unlocks
from .services.reconcile import run as run_reconcile
from .services.pots import summarize_payperiod


app = FastAPI(title="AutoBudget API (lite)", version="0.1.0")


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
