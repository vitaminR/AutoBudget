import React, { useEffect, useState } from "react";
import axios from "axios";
import { API } from "../api/client";
import StatusDisplay from "../components/StatusDisplay";

const getRowClass = (billClass) => {
  switch (billClass) {
    case 'Debt':
      return 'table-danger fw-bold';
    case 'Critical':
      return 'table-danger';
    case 'Needed':
      return 'table-warning';
    case 'Comfort':
      return 'table-info';
    default:
      return '';
  }
};

const Bills = () => {
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchBills = () => {
    setLoading(true);
    axios
      .get(API("/bills"))
      .then((response) => {
        setBills(response.data);
      })
      .catch((err) => {
        console.error("Error fetching bills:", err);
        setError("Failed to load bills. Is the backend server running?");
      })
      .finally(() => {
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchBills();
  }, []);

  const handleTogglePaid = (billId) => {
    const originalBills = [...bills];
    // Optimistic update
    setBills((prevBills) =>
      prevBills.map((b) => (b.id === billId ? { ...b, paid: !b.paid } : b))
    );
    axios
      .post(API(`/bills/${billId}/toggle-paid`))
      .catch((err) => {
        console.error(`Error toggling paid status for bill ${billId}:`, err);
        setError("Failed to update bill status. Reverting change.");
        setBills(originalBills); // Revert on error
      });
  };

  return (
    <div>
      <header className="mb-4">
        <h2>All Bills</h2>
        <p className="text-muted">A complete list of all your bills, color-coded by category.</p>
      </header>

      <StatusDisplay loading={loading} error={error} onDismiss={() => setError(null)} />

      {!loading && (
        <div className="table-responsive">
          <table className="table table-hover">
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
              {bills.length > 0 ? (
                bills.map((bill) => (
                  <tr
                    key={bill.id}
                    className={bill.paid ? "table-success text-body-secondary" : getRowClass(bill.bill_class)}
                  >
                    <td style={{ textDecoration: bill.paid ? "line-through" : "none" }}>
                      {bill.name}
                    </td>
                    <td style={{ textDecoration: bill.paid ? "line-through" : "none" }}>
                      ${bill.amount.toFixed(2)}
                    </td>
                    <td>{bill.due_day}</td>
                    <td>
                      <span className="badge bg-secondary">{bill.bill_class}</span>
                    </td>
                    <td className="text-center">
                      <button
                        className={`btn btn-sm ${bill.paid ? "btn-outline-success" : "btn-primary"}`}
                        onClick={() => handleTogglePaid(bill.id)}
                      >
                        {bill.paid ? "Paid" : "Mark Paid"}
                      </button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="text-center">
                    No bills found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default Bills;