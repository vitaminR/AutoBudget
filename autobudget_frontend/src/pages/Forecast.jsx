import React, { useEffect, useState } from "react";
import { API } from "../api/client";

const Forecast = () => {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const load = async () => {
      try {
        setError(null);
        const res = await fetch(
          API("/payperiods/17/summary").replace("/api", "")
        );
        if (!res.ok) throw new Error("Failed to load");
        const json = await res.json();
        setSummary(json);
      } catch (e) {
        setError(e.message || "Failed");
      }
    };
    load();
  }, []);

  return (
    <div>
      <h2>Forecast</h2>
      {error && <div className="alert alert-danger">{error}</div>}
      {!summary ? (
        <div>Loading…</div>
      ) : (
        <div className="row g-3">
          <div className="col-md-3">
            <div className="card">
              <div className="card-body">
                <h6>Income</h6>
                <div>${summary.income.toFixed(2)}</div>
              </div>
            </div>
          </div>
          <div className="col-md-3">
            <div className="card">
              <div className="card-body">
                <h6>Fixed</h6>
                <div>${summary.fixed.toFixed(2)}</div>
              </div>
            </div>
          </div>
          <div className="col-md-3">
            <div className="card">
              <div className="card-body">
                <h6>Variable</h6>
                <div>${summary.variable.toFixed(2)}</div>
              </div>
            </div>
          </div>
          <div className="col-md-3">
            <div className="card">
              <div className="card-body">
                <h6>Surplus/Deficit</h6>
                <div>${summary.surplus_or_deficit.toFixed(2)}</div>
              </div>
            </div>
          </div>
          <div className="col-12">
            <pre
              style={{
                background: "#111",
                color: "#0f0",
                padding: 12,
                borderRadius: 8,
              }}
            >
              {JSON.stringify(summary.pots, null, 2)}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
};

export default Forecast;
