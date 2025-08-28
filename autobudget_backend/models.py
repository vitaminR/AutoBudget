
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
