import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '../api/client';
import StatusDisplay from '../components/StatusDisplay';

const Paychecks = () => {
  const [paychecks, setPaychecks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // State for the form
  const [source, setSource] = useState('');
  const [amount, setAmount] = useState('');
  const [playerId, setPlayerId] = useState('player1');
  const [editingId, setEditingId] = useState(null);

  const fetchPaychecks = () => {
    setLoading(true);
    axios.get(API('/paychecks'))
      .then(response => {
        setPaychecks(response.data);
      })
      .catch(err => {
        console.error("Error fetching paychecks:", err);
        setError('Failed to load paychecks.');
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchPaychecks();
  }, []);

  const clearForm = () => {
    setSource('');
    setAmount('');
    setPlayerId('player1');
    setEditingId(null);
  };

  const handleEditClick = (paycheck) => {
    setEditingId(paycheck.id);
    setSource(paycheck.source);
    setAmount(paycheck.amount);
    setPlayerId(paycheck.player_id);
  };

  const handleDelete = (paycheckId) => {
    axios.delete(API(`/paychecks/${paycheckId}`))
      .then(() => {
        fetchPaychecks(); // Refresh list after delete
      })
      .catch(err => {
        console.error("Error deleting paycheck:", err);
        setError('Failed to delete paycheck.');
      });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const paycheckData = { source, amount: parseFloat(amount), player_id: playerId };

    const request = editingId
      ? axios.put(API(`/paychecks/${editingId}`), paycheckData)
      : axios.post(API('/paychecks'), paycheckData);

    request
      .then(() => {
        fetchPaychecks(); // Refresh list
        clearForm();
      })
      .catch(err => {
        console.error("Error saving paycheck:", err);
        setError('Failed to save paycheck.');
      });
  };

  return (
    <div>
      <header className="mb-4">
        <h2>Manage Paychecks</h2>
        <p className="text-muted">Add, edit, or remove income sources. This total income is used for budget calculations.</p>
      </header>

      <div className="card mb-4">
        <div className="card-body">
          <h5 className="card-title">{editingId ? 'Edit Paycheck' : 'Add New Paycheck'}</h5>
          <form onSubmit={handleSubmit}>
            <div className="row">
              <div className="col-md-4 mb-3">
                <label htmlFor="source" className="form-label">Income Source</label>
                <input type="text" className="form-control" id="source" value={source} onChange={e => setSource(e.target.value)} placeholder="e.g., My Job" required />
              </div>
              <div className="col-md-3 mb-3">
                <label htmlFor="amount" className="form-label">Amount</label>
                <input type="number" step="0.01" className="form-control" id="amount" value={amount} onChange={e => setAmount(e.target.value)} placeholder="e.g., 2000.00" required />
              </div>
              <div className="col-md-3 mb-3">
                <label htmlFor="player" className="form-label">Player</label>
                <select className="form-select" id="player" value={playerId} onChange={e => setPlayerId(e.target.value)}>
                  <option value="player1">Player 1</option>
                  <option value="player2">Player 2</option>
                </select>
              </div>
              <div className="col-md-2 d-flex align-items-end mb-3">
                <button type="submit" className="btn btn-primary w-100">{editingId ? 'Update' : 'Add'}</button>
                {editingId && <button type="button" className="btn btn-secondary ms-2 w-100" onClick={clearForm}>Cancel</button>}
              </div>
            </div>
          </form>
        </div>
      </div>

      <StatusDisplay loading={loading} error={error} onDismiss={() => setError(null)} />

      <div className="card">
        <div className="card-header">
          <h5>Current Paychecks</h5>
        </div>
        <div className="table-responsive">
          <table className="table table-hover mb-0">
            <thead>
              <tr>
                <th>Source</th>
                <th>Amount</th>
                <th>Player</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {paychecks.map(p => (
                <tr key={p.id}>
                  <td>{p.source}</td>
                  <td>${p.amount.toFixed(2)}</td>
                  <td>{p.player_id}</td>
                  <td>
                    <button className="btn btn-sm btn-outline-secondary me-2" onClick={() => handleEditClick(p)}>Edit</button>
                    <button className="btn btn-sm btn-outline-danger" onClick={() => handleDelete(p.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Paychecks;
