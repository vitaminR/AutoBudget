"""Lightweight FastAPI app exposing minimal endpoints without a database.

Endpoints:
- POST /ingest/bills (UploadFile CSV) -> {"ingested_rows": >= 1}
- GET /payperiods/{pp_id}/summary -> budget summary skeleton with required keys
- GET /debts/snowball -> [{name,balance,apr,payoff_eta_days}]
- GET /unlocks -> [{action,impact_score,prereqs}]
- POST /reconcile -> {"matched": [], "unmatched": payload.transactions}
"""
from __future__ import annotations

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
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
from autobudget_backend import models
from autobudget_backend.db import SessionLocal, engine, init_db

try:
    init_db()
except Exception as e:
    print(f"Error initializing database: {e}")


app = FastAPI(title="AutoBudget API (lite)", version="0.1.0")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
async def ingest_bills(file: UploadFile = File(...), db: Session = Depends(get_db)) -> Dict[str, int]:
    """Parse CSV data and store it in the database.

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
        if has_header:
            header = rows[0]
            data_rows = rows[1:]
            # Map CSV headers to model fields
            header_map = {h.strip().lower(): h.strip() for h in header}
            name_col = header_map.get("name")
            amount_col = header_map.get("amount")
            dueday_col = header_map.get("dueday")
            class_col = header_map.get("class")
            pp_col = header_map.get("pp")
        else:
            # Assume fixed order if no header
            data_rows = rows
            name_col, amount_col, dueday_col, class_col, pp_col = "Name", "Amount", "DueDay", "Class", "PP"

        ingested_count = 0
        for row_data in data_rows:
            if any(cell.strip() for cell in row_data):
                try:
                    bill_data = {
                        "name": row_data[header.index(name_col)],
                        "amount": float(row_data[header.index(amount_col)]),
                        "due_day": int(row_data[header.index(dueday_col)]),
                        "bill_class": row_data[header.index(class_col)],
                        "pp": int(row_data[header.index(pp_col)]),
                    }
                    db_bill = models.Bill(**bill_data)
                    db.add(db_bill)
                    ingested_count += 1
                except (ValueError, IndexError) as e:
                    print(f"Skipping row due to parsing error: {e}")
        db.commit()
        return {"ingested_rows": ingested_count}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid CSV or database error: {e}")


from pydantic import BaseModel

# Pydantic Models (Schemas)
class BillUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    due_day: Optional[int] = None
    bill_class: Optional[str] = None
    pp: Optional[int] = None
    paid: Optional[bool] = None

class BillCreate(BaseModel):
    name: str
    amount: float
    due_day: int
    bill_class: str
    pp: int

class PaycheckBase(BaseModel):
    source: str
    amount: float
    player_id: str

class PaycheckCreate(PaycheckBase):
    pass

class PaycheckUpdate(BaseModel):
    source: Optional[str] = None
    amount: Optional[float] = None
    player_id: Optional[str] = None

@app.post("/paychecks", status_code=201)
def create_paycheck(paycheck: PaycheckCreate, db: Session = Depends(get_db)):
    db_paycheck = models.Paycheck(**paycheck.dict())
    db.add(db_paycheck)
    db.commit()
    db.refresh(db_paycheck)
    return db_paycheck

@app.get("/paychecks")
def get_paychecks(db: Session = Depends(get_db)):
    return db.query(models.Paycheck).all()

@app.put("/paychecks/{paycheck_id}")
def update_paycheck(paycheck_id: int, paycheck: PaycheckUpdate, db: Session = Depends(get_db)):
    db_paycheck = db.query(models.Paycheck).filter(models.Paycheck.id == paycheck_id).first()
    if not db_paycheck:
        raise HTTPException(status_code=404, detail="Paycheck not found")
    update_data = paycheck.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_paycheck, key, value)
    db.commit()
    db.refresh(db_paycheck)
    return db_paycheck

@app.delete("/paychecks/{paycheck_id}", status_code=204)
def delete_paycheck(paycheck_id: int, db: Session = Depends(get_db)):
    db_paycheck = db.query(models.Paycheck).filter(models.Paycheck.id == paycheck_id).first()
    if not db_paycheck:
        raise HTTPException(status_code=404, detail="Paycheck not found")
    db.delete(db_paycheck)
    db.commit()
    return {"ok": True}

@app.post("/bills", status_code=201)
def create_bill(bill: BillCreate, db: Session = Depends(get_db)):
    db_bill = models.Bill(**bill.dict())
    db.add(db_bill)
    db.commit()
    db.refresh(db_bill)
    return db_bill

@app.put("/bills/{bill_id}")
def update_bill(bill_id: int, bill: BillUpdate, db: Session = Depends(get_db)):
    db_bill = db.query(models.Bill).filter(models.Bill.id == bill_id).first()
    if not db_bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    update_data = bill.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_bill, key, value)
    db.commit()
    db.refresh(db_bill)
    return db_bill

@app.delete("/bills/{bill_id}", status_code=204)
def delete_bill(bill_id: int, db: Session = Depends(get_db)):
    db_bill = db.query(models.Bill).filter(models.Bill.id == bill_id).first()
    if not db_bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    db.delete(db_bill)
    db.commit()
    return {"ok": True}


@app.get("/bills")
def get_bills(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Retrieve all bills from the database."""
    bills = db.query(models.Bill).all()
    return [
        {
            "id": bill.id,
            "name": bill.name,
            "amount": bill.amount,
            "due_day": bill.due_day,
            "bill_class": bill.bill_class,
            "pp": bill.pp,
            "paid": bill.paid,
        }
        for bill in bills
    ]


@app.get("/payperiods/{pp_id}/summary")
def payperiod_summary(pp_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Return a real summary for a pay period based on data from the DB."""
    bills = db.query(models.Bill).filter(models.Bill.pp == pp_id).all()
    if not bills:
        raise HTTPException(status_code=404, detail=f"No bills found for pay period {pp_id}")
    summary = summarize_payperiod(db=db, bills=bills)
    summary["pp_id"] = pp_id
    return summary


@app.get("/debts/snowball")
def debts_snowball(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Return a simple snowball ordering with payoff ETA in days.

    Defensive: if called programmatically and `db` is not a Session (for example
    a `Depends` placeholder), create a local SessionLocal() and use that.
    """
    close_after = False
    if not hasattr(db, "query"):
        db = SessionLocal()
        close_after = True
    try:
        debts = db.query(models.Bill).filter(models.Bill.bill_class == 'Credit').all()
        debt_list = [{"name": debt.name, "balance": debt.amount, "apr": 0} for debt in debts]
        return compute_snowball(debt_list)
    finally:
        if close_after:
            db.close()


@app.get("/unlocks")
def get_unlocks(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Return suggested unlock actions with impact and prerequisites."""
    unlocks = suggest_unlocks()
    small_bills = db.query(models.Bill).filter(models.Bill.amount < 100, models.Bill.paid == False).all()
    for bill in small_bills:
        unlocks.append(
            {
                "action": f"Pay off {bill.name}",
                "impact_score": 0.7,
                "prereqs": [f"Budget allows for ${bill.amount} payment"],
            }
        )
    return unlocks


@app.post("/reconcile")
def reconcile(payload: Dict[str, Any], db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Return matched/unmatched for provided transactions without touching a DB."""
    txns = payload.get("transactions") or []
    bills = db.query(models.Bill).all()
    return run_reconcile(txns, bills)


from pydantic import BaseModel
from autobudget_backend.services import gamification

class GameTask(BaseModel):
    player_id: str
    task_type: str

@app.get("/gamification/status", tags=["gamification"])
def get_status() -> Dict[str, Any]:
    """Returns the current points and spending money for both players."""
    return gamification.get_gamification_status()

@app.post("/gamification/complete-task", tags=["gamification"])
def complete_gamification_task(task: GameTask) -> Dict[str, Any]:
    """
    Logs a completed task for a player and returns their updated status.
    """
    try:
        updated_status = gamification.complete_task(
            player_id=task.player_id, task_type=task.task_type
        )
        return updated_status
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/gamification/tasks", tags=["gamification"])
def get_gamification_tasks(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Returns a list of unpaid bills to be used as available tasks."""
    unpaid_bills = db.query(models.Bill).filter(models.Bill.paid == False).all()
    return [
        {
            "id": bill.id,
            "name": bill.name,
            "amount": bill.amount,
            "bill_class": bill.bill_class,
            "task_type": "pay_bill"
        }
        for bill in unpaid_bills
    ]


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
def _compat_pp_bills(pp: int, db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    bills = db.query(models.Bill).filter(models.Bill.pp == pp).all()
    return [
        {
            "id": bill.id,
            "Name": bill.name,
            "Amount": bill.amount,
            "DueDay": bill.due_day,
            "Class": bill.bill_class,
            "PP": bill.pp,
            "paid": bill.paid,
        }
        for bill in bills
    ]


@app.post("/api/bills/{bill_id}/toggle-paid")  # COMPAT
def _compat_toggle(bill_id: int, db: Session = Depends(get_db)) -> Dict[str, Any]:
    bill = db.query(models.Bill).filter(models.Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    bill.paid = not bill.paid
    db.commit()
    return {"ok": True, "id": bill.id, "paid": bill.paid}

# --- COMPAT extras so /api/* works for MVP endpoints too
@app.get("/api/debts/snowball")
def _compat_debts_snowball() -> List[Dict[str, Any]]:
    # Directly implement the snowball compat route to avoid calling the
    # endpoint function (which relies on FastAPI dependency injection).
    db = SessionLocal()
    try:
        debts = db.query(models.Bill).filter(models.Bill.bill_class == 'Credit').all()
        debt_list = [{"name": debt.name, "balance": debt.amount, "apr": 0} for debt in debts]
        return compute_snowball(debt_list)
    finally:
        db.close()

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
