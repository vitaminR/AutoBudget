import React, { useState, useEffect, useMemo } from "react";
import axios from "axios";
import { API } from "../api/client";

const Debt = () => {
  const [debts, setDebts] = useState([]); // raw snowball items
  const [creditBills, setCreditBills] = useState([]); // source bills for editing {id,name,amount}
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Edit modal state
  const [showEdit, setShowEdit] = useState(false);
  const [editName, setEditName] = useState(null);
  const [editCandidates, setEditCandidates] = useState([]); // bills with same name
  const [selectedBillId, setSelectedBillId] = useState(null);
  const [editAmount, setEditAmount] = useState("");

  useEffect(() => {
    // Load snowball + underlying bills (for edit targeting)
    const load = async () => {
      try {
        setLoading(true);
        setError(null);
        const [sbRes, billsRes] = await Promise.all([
          axios.get(API("/debts/snowball")),
          axios.get(API("/bills")),
        ]);
        setDebts(sbRes.data || []);
        // Keep only credit-class bills with id, name, amount
        const credits = (billsRes.data || [])
          .filter((b) => b.bill_class === "Credit")
          .map((b) => ({ id: b.id, name: b.name, amount: b.amount }));
        setCreditBills(credits);
      } catch (err) {
        console.error("Error loading debts/bills:", err);
        setError("Failed to load debt data. Is the backend running?");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  // Group duplicates by debt name for clearer display
  const grouped = useMemo(() => {
    const byName = new Map();
    for (const d of debts) {
      const key = d.name || "Unknown";
      const prev = byName.get(key) || { name: key, total: 0, count: 0 };
      prev.total += Number(d.balance || 0);
      prev.count += 1;
      byName.set(key, prev);
    }
    // compute simple ETA consistent with backend heuristic (300/mo)
    const out = Array.from(byName.values()).map((x) => ({
      name: x.name,
      balance: x.total,
      payoff_eta_days: Math.ceil((x.total || 0) / 300) * 30,
      count: x.count,
    }));
    return out.sort((a, b) => a.balance - b.balance);
  }, [debts]);

  const openEdit = (name) => {
    const candidates = creditBills.filter((b) => b.name === name);
    setEditCandidates(candidates);
    setSelectedBillId(candidates.length ? candidates[0].id : null);
    setEditAmount(candidates.length ? String(candidates[0].amount) : "");
    setEditName(name);
    setShowEdit(true);
  };

  const saveEdit = async () => {
    if (!selectedBillId) {
      setShowEdit(false);
      return;
    }
    const amt = parseFloat(editAmount);
    if (Number.isNaN(amt) || amt < 0) {
      alert("Please enter a valid, non-negative amount.");
      return;
    }
    try {
      await axios.put(API(`/bills/${selectedBillId}`), { amount: amt });
      // refresh both datasets
      const [sbRes, billsRes] = await Promise.all([
        axios.get(API("/debts/snowball")),
        axios.get(API("/bills")),
      ]);
      setDebts(sbRes.data || []);
      const credits = (billsRes.data || [])
        .filter((b) => b.bill_class === "Credit")
        .map((b) => ({ id: b.id, name: b.name, amount: b.amount }));
      setCreditBills(credits);
      setShowEdit(false);
    } catch (err) {
      console.error("Failed to update bill amount:", err);
      alert("Failed to update amount.");
    }
  };

  return (
    <div>
      <header className="mb-4">
        <h2>Debt Snowball</h2>
        <p className="text-muted">
          Your debts ordered by the snowball method (lowest balance first) to
          build momentum.
        </p>
      </header>

      {loading && <p>Loading debt projections...</p>}
      {error && <div className="alert alert-danger">{error}</div>}

      {!loading && !error && (
        <div className="table-responsive">
          <table className="table table-hover">
            <thead className="thead-light">
              <tr>
                <th>Debt Name</th>
                <th>Balance</th>
                <th>Payoff ETA (Days)</th>
                <th className="text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              {grouped.map((debt, index) => (
                <tr key={index}>
                  <td>
                    {debt.name}
                    {debt.count > 1 && (
                      <span
                        className="badge bg-secondary ms-2"
                        title="Number of entries merged"
                      >
                        x{debt.count}
                      </span>
                    )}
                  </td>
                  <td>${debt.balance.toFixed(2)}</td>
                  <td>{debt.payoff_eta_days}</td>
                  <td className="text-center">
                    <button
                      className="btn btn-sm btn-outline-primary"
                      onClick={() => openEdit(debt.name)}
                    >
                      Edit Amount
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Simple inline modal */}
      {showEdit && (
        <div
          className="position-fixed top-0 start-0 w-100 h-100"
          style={{ background: "rgba(0,0,0,0.5)", zIndex: 1050 }}
        >
          <div className="container h-100 d-flex align-items-center justify-content-center">
            <div className="card" style={{ minWidth: 360 }}>
              <div className="card-header d-flex justify-content-between align-items-center">
                <strong>Edit Amount</strong>
                <button
                  className="btn btn-sm btn-outline-secondary"
                  onClick={() => setShowEdit(false)}
                >
                  Close
                </button>
              </div>
              <div className="card-body">
                <div className="mb-3">
                  <label className="form-label">Debt Name</label>
                  <input
                    className="form-control"
                    value={editName || ""}
                    disabled
                  />
                </div>
                {editCandidates.length > 1 && (
                  <div className="mb-3">
                    <label className="form-label">Select Entry</label>
                    <select
                      className="form-select"
                      value={selectedBillId || ""}
                      onChange={(e) => {
                        const id = Number(e.target.value);
                        setSelectedBillId(id);
                        const found = editCandidates.find((c) => c.id === id);
                        if (found) setEditAmount(String(found.amount));
                      }}
                    >
                      {editCandidates.map((c) => (
                        <option key={c.id} value={c.id}>
                          #{c.id} — {c.name}
                        </option>
                      ))}
                    </select>
                  </div>
                )}
                <div className="mb-3">
                  <label className="form-label">New Amount</label>
                  <input
                    type="number"
                    step="0.01"
                    className="form-control"
                    value={editAmount}
                    onChange={(e) => setEditAmount(e.target.value)}
                  />
                </div>
                <div className="d-flex justify-content-end gap-2">
                  <button
                    className="btn btn-secondary"
                    onClick={() => setShowEdit(false)}
                  >
                    Cancel
                  </button>
                  <button className="btn btn-primary" onClick={saveEdit}>
                    Save
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Debt;
