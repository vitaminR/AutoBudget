"""Pay period summary utilities."""
from __future__ import annotations

from typing import Dict, List
from sqlalchemy.orm import Session
from .. import models


def summarize_payperiod(db: Session, bills: List[models.Bill]) -> Dict[str, object]:
    """Return a summary for a pay period based on real data from the database."""
    # Calculate total income from all paychecks
    paychecks = db.query(models.Paycheck).all()
    income = sum(p.amount for p in paychecks)

    # Calculate fixed and variable costs from the bills for the period
    fixed = sum(b.amount for b in bills if b.bill_class in ['Debt', 'Critical'])
    variable = sum(b.amount for b in bills if b.bill_class in ['Needed', 'Comfort'])
    surplus = round(income - fixed - variable, 2)

    # Pots are based on the budgeted income allocation
    pots = {
        "Debt_Payments": round(income * 0.10, 2),
        "Critical_Bills": round(income * 0.30, 2),
        "Needed_Bills": round(income * 0.15, 2),
        "Comfort_Pool": round(income * 0.10, 2),
        "Annual_Rainy_Day": round(income * 0.10, 2),
    }
    # Note: The remaining 25% is available for the gamification/spending pool

    return {
        "income": income,
        "fixed": fixed,
        "variable": variable,
        "surplus_or_deficit": surplus,
        "pots": pots,
    }