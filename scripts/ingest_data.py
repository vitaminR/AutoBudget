
import os
import logging
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, timedelta

# This script reuses the database models and configuration from the FastAPI backend
# to populate the database from the CSV file.

# --- Configuration ---
# Ensure paths are resolved from the project root to run this script from anywhere
ROOT_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{ROOT_DIR / 'autobudget.db'}")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH", str(ROOT_DIR / "data/5.Tidy_Bills_AugNov_with_PPs.csv"))
PAY_PERIOD_ANCHOR_DATE = date.fromisoformat(os.getenv("PAY_PERIOD_ANCHOR_DATE", "2025-08-04"))

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ingestion_script")

# --- SQLAlchemy Setup ---
# We need to import the Base and the DB models from the backend's main.py
# To do this without creating circular dependencies, we can add the backend dir to sys.path
# but a cleaner way for a script is to redefine the necessary components.
from sqlalchemy import Column, Integer, String, Float, Boolean, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

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

def ingest_data():
    """Connects to the DB, wipes the tables, and repopulates from the CSV."""
    logger.info(f"Connecting to database at {DATABASE_URL}")
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    logger.info("Creating all tables...")
    Base.metadata.create_all(bind=engine)

    try:
        logger.info(f"Reading CSV file from {CSV_FILE_PATH}")
        df = pd.read_csv(CSV_FILE_PATH)
    except FileNotFoundError:
        logger.error(f"FATAL: CSV file not found at {CSV_FILE_PATH}")
        return

    logger.info("Wiping existing data from bills and pay_periods tables...")
    db.query(BillDB).delete()
    db.query(PayPeriodDB).delete()

    logger.info(f"Ingesting {len(df)} new bill records...")
    for _, row in df.iterrows():
        bill = BillDB(**row.to_dict(), paid=False)
        db.add(bill)

    unique_pps = sorted(df["PP"].unique())
    logger.info(f"Ingesting {len(unique_pps)} new pay period records...")
    for pp_num in unique_pps:
        offset = int(pp_num - unique_pps[0])
        start_date = PAY_PERIOD_ANCHOR_DATE + timedelta(weeks=2 * offset)
        end_date = start_date + timedelta(days=13)
        pp_entry = PayPeriodDB(pp_number=pp_num, start_date=start_date, end_date=end_date)
        db.add(pp_entry)
    
    try:
        db.commit()
        logger.info("Successfully committed all new data to the database!")
    except Exception as e:
        logger.error(f"Failed to commit data: {e}")
        db.rollback()
    finally:
        db.close()
        logger.info("Database session closed.")

if __name__ == "__main__":
    ingest_data()
