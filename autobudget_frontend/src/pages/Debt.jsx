import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '../api/client';

const Debt = () => {
  const [debts, setDebts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    axios.get(API('/debts/snowball'))
      .then(response => {
        setDebts(response.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching debt snowball:", err);
        setError('Failed to load debt projections. Is the backend running?');
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <header className="mb-4">
        <h2>Debt Snowball</h2>
        <p className="text-muted">Your debts ordered by the snowball method (lowest balance first) to build momentum.</p>
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
              </tr>
            </thead>
            <tbody>
              {debts.map((debt, index) => (
                <tr key={index}>
                  <td>{debt.name}</td>
                  <td>${debt.balance.toFixed(2)}</td>
                  <td>{debt.payoff_eta_days}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Debt;
