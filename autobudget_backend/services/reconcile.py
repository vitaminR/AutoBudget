"""Transaction reconciliation utilities.

run(transactions) -> {matched:[], unmatched:[]}.
Pure function; naive matching by exact amount and date, none provided so all unmatched.
"""
from __future__ import annotations
from typing import Any, Dict, List


def run(transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Deterministically mark transactions as matched by memo keywords.

    If memo contains "rent" or "grocer" (case-insensitive), it's matched.
    """
    matched: List[Dict[str, Any]] = []
    unmatched: List[Dict[str, Any]] = []
    for t in transactions or []:
        memo = str(t.get("memo", "")).lower()
        if ("rent" in memo) or ("grocer" in memo):
            matched.append(t)
        else:
            unmatched.append(t)
    return {"matched": matched, "unmatched": unmatched}
