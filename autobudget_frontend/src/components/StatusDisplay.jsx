import React from "react";

const StatusDisplay = ({ loading = false, error = null, onDismiss }) => {
  if (loading)
    return (
      <div className="text-center py-3">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  if (error)
    return (
      <div className="alert alert-danger" role="alert" onClick={onDismiss}>
        {error} {onDismiss ? "(click to dismiss)" : null}
      </div>
    );
  return null;
};

export default StatusDisplay;
