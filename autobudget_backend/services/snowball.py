"""Debt snowball computation utilities.

compute(debts) -> list of {name,balance,apr,payoff_eta_days} sorted by balance.
Pure function; no I/O.
"""
from __future__ import annotations
from typing import List, Dict, Any
import math


def compute(debts: List[Dict[str, Any]], monthly_payment: float = 300.0) -> List[Dict[str, Any]]:
    """Return debts sorted by smallest balance with robust payoff ETA in days.

    ETA = ceil(balance / max(1, monthly_payment)) * 30 days.
    """
    cleaned = []
    for d in debts:
        bal = float(d.get("balance", 0) or 0)
        eta_months = math.ceil(bal / max(1.0, monthly_payment))
        eta_days = int(eta_months * 30)
        cleaned.append({
            "name": d.get("name", ""),
            "balance": bal,
            "apr": float(d.get("apr", 0) or 0),
            "payoff_eta_days": eta_days,
        })
    return sorted(cleaned, key=lambda x: x["balance"])
