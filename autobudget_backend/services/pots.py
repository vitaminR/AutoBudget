"""Deterministic, DB-free pay period summary utilities.

summarize_payperiod(pp_id) -> dict with required budget keys and pots.
Pure function with stable placeholder math so tests pass consistently.
"""
from __future__ import annotations

from typing import Dict


def summarize_payperiod(pp_id: str) -> Dict[str, object]:
    """Return a deterministic summary for a pay period without a DB.

    Uses pp_id digits to vary income in a stable way, then applies fixed ratios.
    Keys: income, fixed, variable, surplus_or_deficit, pots{Needs,Wants,Savings,Debt}.
    """
    digits = "".join(ch for ch in str(pp_id) if ch.isdigit()) or "0"
    n = int(digits)
    income = float(2000.0 + (n % 5) * 100.0)
    fixed = round(income * 0.50, 2)
    variable = round(income * 0.30, 2)
    surplus = round(income - fixed - variable, 2)
    pots = {
        "Needs": round(income * 0.50, 2),
        "Wants": round(income * 0.30, 2),
        "Savings": round(income * 0.15, 2),
        "Debt": round(income * 0.05, 2),
    }
    return {
        "income": income,
        "fixed": fixed,
        "variable": variable,
        "surplus_or_deficit": surplus,
        "pots": pots,
    }
