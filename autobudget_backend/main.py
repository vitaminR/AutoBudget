
import os
import logging
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, Date
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import date, timedelta

# --- Configuration ---
# Resolve project root and use absolute DB/CSV paths to avoid path confusion when reloader/WSL changes cwd
ROOT_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{ROOT_DIR / 'autobudget.db'}")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH", str(ROOT_DIR / "data/5.Tidy_Bills_AugNov_with_PPs.csv"))
PAY_PERIOD_ANCHOR_DATE = date.fromisoformat(os.getenv("PAY_PERIOD_ANCHOR_DATE", "2025-08-04"))

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("autobudget")

# --- SQLAlchemy Setup ---
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Models ---
class BillDB(Base):
    __tablename__ = "bills"
    id = Column(Integer, primary_key=True, index=True)
    Name = Column(String, index=True)
    Month = Column(String)
    Amount = Column(Float)
    DueDay = Column(Integer)
    Class = Column(String)
    PP = Column(Integer, index=True)
    paid = Column(Boolean, default=False)

class PayPeriodDB(Base):
    __tablename__ = "pay_periods"
    id = Column(Integer, primary_key=True, index=True)
    pp_number = Column(Integer, unique=True, index=True)
    start_date = Column(Date)
    end_date = Column(Date)

# --- Pydantic Models ---
class Bill(BaseModel):
    id: int
    Name: str
    Month: str
    Amount: float
    DueDay: int
    Class: str
    PP: int
    paid: bool

    # Pydantic v2: use model_config to replace the old `orm_mode`
    model_config = ConfigDict(from_attributes=True)

class PayPeriod(BaseModel):
    id: int
    pp_number: int
    start_date: date
    end_date: date

    model_config = ConfigDict(from_attributes=True)

# --- Application Setup ---
app = FastAPI(
    title="AutoBudget API",
    description="API for managing budget data with a database.",
    version="0.3.0",
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# --- Database Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Log full exception for diagnostics but return a friendly 503 to clients
    logger.exception("Unhandled error processing request: %s %s", request.method, request.url)
    return JSONResponse(status_code=503, content={"detail": "Server error, please try again later."})

# --- API Endpoints ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the AutoBudget API. Go to /docs for documentation."}

@app.post("/api/ingest-csv", status_code=201)
def ingest_csv_data(db: Session = Depends(get_db)):
    try:
        df = pd.read_csv(CSV_FILE_PATH)
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"CSV file not found at {CSV_FILE_PATH}")

    db.query(BillDB).delete()
    db.query(PayPeriodDB).delete()

    for _, row in df.iterrows():
        bill = BillDB(**row.to_dict(), paid=False)
        db.add(bill)

    unique_pps = sorted(df["PP"].unique())

    for pp_num in unique_pps:
        offset = pp_num - unique_pps[0]
        start_date = PAY_PERIOD_ANCHOR_DATE + timedelta(weeks=2 * offset)
        end_date = start_date + timedelta(days=13)
        pp_entry = PayPeriodDB(pp_number=pp_num, start_date=start_date, end_date=end_date)
        db.add(pp_entry)
    
    db.commit()
    return {"message": f"Successfully ingested {len(df)} bills and {len(unique_pps)} pay periods."}

@app.get("/api/pay-periods", response_model=List[PayPeriod])
def get_pay_periods(db: Session = Depends(get_db)):
    return db.query(PayPeriodDB).order_by(PayPeriodDB.pp_number).all()

@app.get("/api/pay-periods/{period_number}/bills", response_model=List[Bill])
def get_bills_for_pay_period(period_number: int, db: Session = Depends(get_db)):
    bills = db.query(BillDB).filter(BillDB.PP == period_number).order_by(BillDB.DueDay).all()
    if not bills:
        raise HTTPException(status_code=404, detail=f"No bills found for pay period {period_number}.")
    return bills

@app.post("/api/bills/{bill_id}/toggle-paid", response_model=Bill)
def toggle_bill_paid_status(bill_id: int, db: Session = Depends(get_db)):
    bill = db.query(BillDB).filter(BillDB.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail=f"Bill with id {bill_id} not found.")
    
    bill.paid = not bill.paid
    db.commit()
    db.refresh(bill)
    return bill
