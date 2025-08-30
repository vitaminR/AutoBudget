from sqlalchemy import Column, Integer, String, Float, Boolean
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