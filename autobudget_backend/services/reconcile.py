"""Transaction reconciliation utilities.

run(transactions) -> {matched:[], unmatched:[]}.
Pure function; naive matching by exact amount and date, none provided so all unmatched.
"""
from __future__ import annotations
from typing import Any, Dict, List


def run(transactions: List[Dict[str, Any]], bills: List[Any]) -> Dict[str, Any]:
    """Deterministically mark transactions as matched by bill names.

    If memo contains a bill name (case-insensitive), it's matched.
    """
    matched: List[Dict[str, Any]] = []
    unmatched: List[Dict[str, Any]] = []
    bill_names = [bill.name.lower() for bill in bills]
    for t in transactions or []:
        memo = str(t.get("memo", "")).strip().lower()
        if any(bill_name in memo for bill_name in bill_names):
            matched.append(t)
        else:
            unmatched.append(t)
    result: Dict[str, Any] = {"matched": matched, "unmatched": unmatched}
    # UC-006 acceptance: also expose counts for tests/automation
    result["matched_count"] = len(matched)
    result["unmatched_count"] = len(unmatched)
    return result
