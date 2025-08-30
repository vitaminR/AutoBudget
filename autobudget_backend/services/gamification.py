"""Service for managing the gamification system."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

# Define the path for the gamification state file
_STATE_FILE = Path(__file__).resolve().parents[2] / ".devdata" / "gamification_state.json"

# Define points for different tasks
TASK_POINTS = {
    "pay_bill": 10,
    "reconcile": 20,
    "forecast": 15,
    "edit_budget": 5,
}

def _get_default_state() -> Dict[str, Any]:
    """Return the default state for the gamification system."""
    return {
        "player1": {"points": 0, "spending_money": 0.0},
        "player2": {"points": 0, "spending_money": 0.0},
    }

def _get_state() -> Dict[str, Any]:
    """Reads the gamification state from the JSON file."""
    if not _STATE_FILE.exists():
        return _get_default_state()
    try:
        with _STATE_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return _get_default_state()

def _save_state(state: Dict[str, Any]) -> None:
    """Saves the gamification state to the JSON file."""
    try:
        _STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with _STATE_FILE.open("w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except IOError as e:
        print(f"Error saving gamification state: {e}")


def get_gamification_status() -> Dict[str, Any]:
    """Returns the current status of all players."""
    return _get_state()

def complete_task(player_id: str, task_type: str) -> Dict[str, Any]:
    """
    Updates a player's score based on a completed task.
    A simple rule: 100 points = $1 of spending money.
    """
    if player_id not in ["player1", "player2"]:
        raise ValueError("Invalid player_id")
    
    points_to_award = TASK_POINTS.get(task_type, 0)
    if points_to_award == 0:
        raise ValueError("Invalid task_type")

    state = _get_state()
    
    # Award points
    state[player_id]["points"] += points_to_award
    
    # Update spending money based on points
    # Example: Every 100 points converts to $1.00
    state[player_id]["spending_money"] = (state[player_id]["points"] // 100) * 1.0
    
    _save_state(state)
    return state[player_id]
