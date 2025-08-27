"""Unlock suggestion utilities.

suggest(context=None) -> list[{action, impact_score, prereqs}].
Pure function; returns a small, static suggestion list for now.
"""
from __future__ import annotations
from typing import Any, Dict, List


def suggest(context: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
    """Return deterministic unlock actions sorted by impact_score (desc)."""
    items = [
        {
            "action": "Pause non-essential subscriptions",
            "impact_score": 0.8,
            "prereqs": ["Review subscription list"],
        },
        {
            "action": "Call provider for rate reduction",
            "impact_score": 0.6,
            "prereqs": ["Recent on-time payments"],
        },
        {
            "action": "Sell one unused item",
            "impact_score": 0.5,
            "prereqs": ["Identify item", "List locally"],
        },
    ]
    return sorted(items, key=lambda x: x["impact_score"], reverse=True)
