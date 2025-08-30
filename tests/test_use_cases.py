import os
import json
import pytest
from fastapi.testclient import TestClient

from autobudget_backend.app import app

client = TestClient(app)


@pytest.mark.order(1)
def test_uc002_summary_shape():
    r = client.get("/payperiods/17/summary")
    assert r.status_code == 200
    body = r.json()
    for key in ["income", "fixed", "variable", "surplus_or_deficit", "pots"]:
        assert key in body


@pytest.mark.order(2)
def test_uc003_pots_keys():
    r = client.get("/payperiods/17/summary")
    assert r.status_code == 200
    body = r.json()
    pots = body.get("pots", {})
    for key in ["Debt_Payments", "Critical_Bills", "Needed_Bills", "Comfort_Pool", "Annual_Rainy_Day"]:
        assert key in pots


@pytest.mark.order(3)
def test_uc004_snowball_sorted():
    r = client.get("/debts/snowball")
    assert r.status_code == 200
    items = r.json()
    balances = [i.get("balance", 0) for i in items]
    assert balances == sorted(balances)
    assert all("payoff_eta_days" in i for i in items)


@pytest.mark.order(4)
def test_uc005_unlocks_shape():
    r = client.get("/unlocks")
    assert r.status_code == 200
    items = r.json()
    assert isinstance(items, list)
    assert items and {"action", "impact_score", "prereqs"}.issubset(items[0].keys())


@pytest.mark.order(5)
def test_uc006_reconcile_counts():
    payload = {"transactions": [{"date": "2025-08-10", "amount": -12.34, "memo": "Coffee"}]}
    r = client.post("/reconcile", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert {"matched", "unmatched"}.issubset(data.keys())


@pytest.mark.order(6)
def test_uc007_gamification_status():
    """Ensure the gamification status endpoint returns the correct shape."""
    r = client.get("/gamification/status")
    assert r.status_code == 200
    data = r.json()
    assert "player1" in data
    assert "player2" in data
    assert "points" in data["player1"]
    assert "spending_money" in data["player1"]

@pytest.mark.order(7)
def test_uc008_gamification_tasks():
    """Ensure the gamification tasks endpoint returns a list."""
    r = client.get("/gamification/tasks")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)

@pytest.mark.order(8)
def test_error_on_nonexistent_payperiod():
    """Ensure requesting a non-existent pay period summary returns 404."""
    # Assuming no pay period 999 exists
    r = client.get("/payperiods/999/summary")
    assert r.status_code == 404

@pytest.mark.order(9)
def test_error_on_bad_gamification_task():
    """Ensure completing a non-existent task type for a player returns 400."""
    payload = {"player_id": "player1", "task_type": "non_existent_task"}
    r = client.post("/gamification/complete-task", json=payload)
    assert r.status_code == 400


@pytest.mark.order(10)
def test_dashboard_loads():
    """
    Ensure the main dashboard endpoints load successfully.
    This is a regression test for the "Failed to load dashboard data" error.
    """
    # The dashboard calls two endpoints, we test them both.
    summary_r = client.get("/payperiods/17/summary")
    assert summary_r.status_code == 200

    snowball_r = client.get("/debts/snowball")
    assert snowball_r.status_code == 200