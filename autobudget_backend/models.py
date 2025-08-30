from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, ForeignKey
from .db import Base

class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    amount = Column(Float)
    due_day = Column(Integer)
    bill_class = Column(String)
    pp = Column(Integer)
    paid = Column(Boolean, default=False)

class Paycheck(Base):
    __tablename__ = "paychecks"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)
    amount = Column(Float)
    player_id = Column(String, index=True) # "player1" or "player2"

class PayPeriod(Base):
    __tablename__ = "pay_periods"

    id = Column(Integer, primary_key=True, index=True)
    pp_number = Column(Integer, unique=True, index=True)
    start_date = Column(Date)
    end_date = Column(Date)

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"))
    sent_at = Column(DateTime)
    reminder_type = Column(String) # e.g., "due_in_3_days"
