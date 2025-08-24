import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api';

// Helper to format dates
const formatDate = (dateString) => {
  const options = { month: 'short', day: 'numeric' };
  // Add T00:00:00 to ensure the date is parsed as local time, not UTC
  return new Date(dateString + 'T00:00:00').toLocaleDateString('en-US', options);
};

function App() {
  const [payPeriods, setPayPeriods] = useState([]);
  const [selectedPeriod, setSelectedPeriod] = useState('');
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState({ periods: false, bills: false });
  const [error, setError] = useState(null);

  // Fetch Pay Periods
  useEffect(() => {
    setLoading(prev => ({ ...prev, periods: true }));
    axios.get(`${API_BASE_URL}/pay-periods`)
      .then(response => {
        setPayPeriods(response.data);
        if (response.data.length > 0) {
          setSelectedPeriod(response.data[0].pp_number);
        }
      })
      .catch(err => {
        console.error('Error fetching pay periods:', err);
        setError('Failed to load pay periods. Is the backend server running?');
      })
      .finally(() => {
        setLoading(prev => ({ ...prev, periods: false }));
      });
  }, []);

  // Fetch Bills for Selected Pay Period
  const fetchBills = useCallback(() => {
    if (!selectedPeriod) return;
    setLoading(prev => ({ ...prev, bills: true }));
    axios.get(`${API_BASE_URL}/pay-periods/${selectedPeriod}`)
      .then(response => {
        setBills(response.data);
      })
      .catch(err => {
        console.error(`Error fetching bills for period ${selectedPeriod}:`, err);
        setError(`Failed to load bills for pay period ${selectedPeriod}.`);
      })
      .finally(() => {
        setLoading(prev => ({ ...prev, bills: false }));
      });
  }, [selectedPeriod]);

  useEffect(() => {
    fetchBills();
  }, [fetchBills]);

  // Handler for toggling the paid status
  const handleTogglePaid = (billId) => {
    const originalBills = [...bills];
    // Optimistically update the UI
    setBills(prevBills =>
      prevBills.map(b => b.id === billId ? { ...b, paid: !b.paid } : b)
    );

    axios.post(`${API_BASE_URL}/bills/${bill_id}/toggle-paid`)
      .catch(err => {
        console.error(`Error toggling paid status for bill ${billId}:`, err);
        setError('Failed to update bill status. Reverting change.');
        // Revert the UI change on error
        setBills(originalBills);
      });
  };

  return (
    <div className="container mt-4">
      <header className="text-center mb-4">
        <h1>AutoBudget</h1>
        <p className="lead">A simple way to track your bills per pay period.</p>
      </header>

      {error && <div className="alert alert-danger" role="alert" onClick={() => setError(null)}>{error} (click to dismiss)</div>}
      
      <div className="row">
        <div className="col-lg-4 mb-4">
          <div className="card">
            <div className="card-body">
              <h5 className="card-title">Select Pay Period</h5>
              {loading.periods ? <p>Loading periods...</p> :
                <select 
                  className="form-select" 
                  onChange={(e) => setSelectedPeriod(Number(e.target.value))} 
                  value={selectedPeriod}
                  disabled={loading.periods}
                >
                  {payPeriods.map(pp => (
                    <option key={pp.pp_number} value={pp.pp_number}>
                      {formatDate(pp.start_date)} - {formatDate(pp.end_date)} (PP {pp.pp_number})
                    </option>
                  ))}
                </select>
              }
            </div>
          </div>
        </div>

        <div className="col-lg-8">
          <h3>Bills for Pay Period {selectedPeriod}</h3>
          {loading.bills ? <p>Loading bills...</p> :
            <div className="table-responsive">
              <table className="table table-striped table-hover">
                <thead className="thead-dark">
                  <tr>
                    <th>Name</th>
                    <th>Amount</th>
                    <th>Due Day</th>
                    <th>Class</th>
                    <th className="text-center">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {bills.length > 0 ? bills.map(bill => (
                    <tr key={bill.id} className={bill.paid ? 'table-success text-body-secondary' : ''}>
                      <td style={{ textDecoration: bill.paid ? 'line-through' : 'none' }}>
                        {bill.Name}
                      </td>
                      <td style={{ textDecoration: bill.paid ? 'line-through' : 'none' }}>
                        ${bill.Amount.toFixed(2)}
                      </td>
                      <td>{bill.DueDay}</td>
                      <td><span className="badge bg-secondary">{bill.Class}</span></td>
                      <td className="text-center">
                        <button 
                          className={`btn btn-sm ${bill.paid ? 'btn-outline-success' : 'btn-primary'}`}
                          onClick={() => handleTogglePaid(bill.id)}
                        >
                          {bill.paid ? 'Paid' : 'Mark Paid'}
                        </button>
                      </td>
                    </tr>
                  )) : <tr><td colSpan="5" className="text-center">No bills for this period.</td></tr>}
                </tbody>
              </table>
            </div>
          }
        </div>
      </div>
    </div>
  );
}

export default App;