import React from "react";

const StatusDisplay = ({ loading = false, error = null, onDismiss }) => {
  if (loading)
    return (
      <div className="text-center py-3">
        <div
          className="spinner-border"
          style={{ color: "var(--brand-accent)" }}
          role="status"
        >
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  if (error)
    return (
      <div
        className="alert"
        role="alert"
        onClick={onDismiss}
        style={{
          backgroundColor: "#3a1b1b",
          border: "1px solid rgba(212,175,55,0.35)",
          color: "var(--brand-text)",
        }}
      >
        {error} {onDismiss ? "(click to dismiss)" : null}
      </div>
    );
  return null;
};

export default StatusDisplay;
