import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import { API } from "../api/client";

const Card = ({ title, value, linkTo, linkText }) => (
  <div className="col-md-3">
    <div className="card shadow-sm">
      <div className="card-body">
        <h6 className="text-muted mb-2">{title}</h6>
        <div className="h4 mb-3">{value}</div>
        {linkTo && (
          <Link className="btn btn-sm btn-outline-primary" to={linkTo}>
            {linkText || "View"}
          </Link>
        )}
      </div>
    </div>
  </div>
);

const Dashboard = () => {
  const [summary, setSummary] = useState(null);
  const [debts, setDebts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        setError(null);
        setLoading(true);

        const [summaryRes, debtsRes] = await axios.all([
          axios.get(API("/payperiods/17/summary")),
          axios.get(API("/debts/snowball")),
        ]);

        setSummary(summaryRes.data);
        setDebts(debtsRes.data);
      } catch (e) {
        const errorMsg = e.response ? e.response.data.detail : e.message;
        setError(errorMsg || "Failed to load dashboard data.");
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, []);

  const upcoming = [
    { label: "Next Pay Period", value: "Aug 18 - Aug 31" },
    { label: "Upcoming Bills", value: "2 in next PP" },
  ];

  return (
    <div>
      <div className="d-flex align-items-center justify-content-between mb-3">
        <div>
          <h2 className="mb-0">Dashboard</h2>
          <p className="text-muted mb-0">Quick view of your budget and debts</p>
        </div>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="row g-3 mb-4">
        <div className="col-md-4">
          <div className="card shadow-sm">
            <div className="card-body">
              <h6 className="text-muted mb-2">Total Monthly Bills</h6>
              <div className="h4">$1,234.56</div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card shadow-sm">
            <div className="card-body">
              <h6 className="text-muted mb-2">Next Bill Due</h6>
              <div className="h4">Sep 05</div>
            </div>
          </div>
        </div>
        <div className="col-md-4">
          <div className="card shadow-sm">
            <div className="card-body">
              <h6 className="text-muted mb-2">Accounts Reconciled</h6>
              <div className="h4">3 / 4</div>
            </div>
          </div>
        </div>
      </div>

      <div className="row g-3 mb-4">
        <Card
          title="Income"
          value={summary ? `$${summary.income.toFixed(2)}` : "…"}
          linkTo="/forecast"
          linkText="Forecast"
        />
        <Card
          title="Fixed"
          value={summary ? `$${summary.fixed.toFixed(2)}` : "…"}
          linkTo="/forecast"
        />
        <Card
          title="Variable"
          value={summary ? `$${summary.variable.toFixed(2)}` : "…"}
          linkTo="/forecast"
        />
        <Card
          title="Surplus/Deficit"
          value={summary ? `$${summary.surplus_or_deficit.toFixed(2)}` : "…"}
          linkTo="/forecast"
        />
      </div>

      <div className="row g-3">
        <div className="col-lg-6">
          <div className="card shadow-sm">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <h5 className="mb-0">Upcoming</h5>
                <Link to="/bills" className="btn btn-sm btn-outline-secondary">
                  Bills
                </Link>
              </div>
              <ul className="list-group list-group-flush">
                {upcoming.map((u, i) => (
                  <li
                    key={i}
                    className="list-group-item d-flex justify-content-between align-items-center"
                  >
                    <span>{u.label}</span>
                    <span className="badge bg-light text-dark">{u.value}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
        <div className="col-lg-6">
          <div className="card shadow-sm">
            <div className="card-body">
              <div className="d-flex justify-content-between align-items-center mb-2">
                <h5 className="mb-0">Debt Snowball</h5>
                <Link to="/debts" className="btn btn-sm btn-outline-secondary">
                  Details
                </Link>
              </div>
              {!debts.length ? (
                <div className="text-muted">Loading…</div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-sm">
                    <thead>
                      <tr>
                        <th>Debt</th>
                        <th>Balance</th>
                        <th>ETA</th>
                      </tr>
                    </thead>
                    <tbody>
                      {debts.slice(0, 3).map((d, i) => (
                        <tr key={i}>
                          <td>{d.name}</td>
                          <td>${d.balance.toFixed(2)}</td>
                          <td>{d.payoff_eta_days} days</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
