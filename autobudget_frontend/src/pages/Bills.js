import React, { useEffect, useState } from "react";
import axios from "axios";
import { API } from "../api/client";
import StatusDisplay from "../components/StatusDisplay";
import { Modal, Button, Form } from "react-bootstrap";

const getRowClass = (billClass) => {
  switch (billClass) {
    case "Debt":
      return "table-danger fw-bold";
    case "Critical":
      return "table-danger";
    case "Needed":
      return "table-warning";
    case "Comfort":
      return "table-info";
    default:
      return "";
  }
};

const Bills = () => {
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [editingBill, setEditingBill] = useState(null);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);

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
    // optimistic UI update
    setBills((prevBills) =>
      prevBills.map((b) => (b.id === billId ? { ...b, paid: !b.paid } : b))
    );
    const updated = bills.find((b) => b.id === billId);
    const nextPaid = updated ? !updated.paid : true;
    axios.put(API(`/bills/${billId}`), { paid: nextPaid }).catch((err) => {
      console.error(`Error updating paid status for bill ${billId}:`, err);
      setError("Failed to update bill status. Reverting change.");
      setBills(originalBills);
    });
  };

  const handleDelete = (billId) => {
    if (window.confirm("Are you sure you want to delete this bill?")) {
      axios
        .delete(API(`/bills/${billId}`))
        .then(() => {
          fetchBills(); // Refresh list
        })
        .catch((err) => {
          console.error("Error deleting bill:", err);
          setError("Failed to delete bill.");
        });
    }
  };

  const handleEdit = (bill) => {
    setEditingBill(bill);
    setIsEditModalOpen(true);
  };

  const handleUpdate = () => {
    if (!editingBill) return;
    axios
      .put(API(`/bills/${editingBill.id}`), editingBill)
      .then(() => {
        setIsEditModalOpen(false);
        setEditingBill(null);
        fetchBills();
      })
      .catch((err) => {
        console.error("Error updating bill:", err);
        setError("Failed to update bill.");
      });
  };

  const handleCloseModal = () => {
    setIsEditModalOpen(false);
    setEditingBill(null);
  };

  return (
    <div>
      <header className="mb-4 d-flex justify-content-between align-items-center">
        <div>
          <h2>All Bills</h2>
          <p className="text-muted mb-0">
            A complete list of all your bills, color-coded by category.
          </p>
        </div>
        <button className="btn btn-primary">Add New Bill</button>{" "}
        {/* Placeholder for future modal */}
      </header>

      <StatusDisplay
        loading={loading}
        error={error}
        onDismiss={() => setError(null)}
      />

      {!loading && (
        <div className="table-responsive">
          <table className="table table-hover">
            <thead className="thead-dark">
              <tr>
                <th>Name</th>
                <th>Amount</th>
                <th>Due Day</th>
                <th>Class</th>
                <th className="text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              {bills.length > 0 ? (
                bills.map((bill) => (
                  <tr
                    key={bill.id}
                    className={
                      bill.paid
                        ? "table-paid"
                        : getRowClass(bill.bill_class)
                    }
                  >
                    <td
                      style={{
                        textDecoration: bill.paid ? "line-through" : "none",
                      }}
                    >
                      {bill.name}
                    </td>
                    <td
                      style={{
                        textDecoration: bill.paid ? "line-through" : "none",
                      }}
                    >
                      ${bill.amount.toFixed(2)}
                    </td>
                    <td>{bill.due_day}</td>
                    <td>
                      <span className="badge bg-secondary">
                        {bill.bill_class}
                      </span>
                    </td>
                    <td className="text-center">
                      <div className="btn-group btn-group-sm" role="group">
                        <button
                          className={`btn ${
                            bill.paid ? "btn-outline-success" : "btn-success"
                          }`}
                          onClick={() => handleTogglePaid(bill.id)}
                        >
                          {bill.paid ? "Paid" : "Marked as Paid"}
                        </button>
                        <button
                          className="btn btn-outline-secondary"
                          onClick={() => handleEdit(bill)}
                        >
                          Edit
                        </button>
                        <button
                          className="btn btn-outline-danger"
                          onClick={() => handleDelete(bill.id)}
                        >
                          Delete
                        </button>
                      </div>
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

      {editingBill && (
        <Modal show={isEditModalOpen} onHide={handleCloseModal}>
          <Modal.Header closeButton>
            <Modal.Title>Edit Bill</Modal.Title>
          </Modal.Header>
          <Modal.Body>
            <Form>
              <Form.Group className="mb-3">
                <Form.Label>Name</Form.Label>
                <Form.Control
                  type="text"
                  value={editingBill.name}
                  onChange={(e) =>
                    setEditingBill({ ...editingBill, name: e.target.value })
                  }
                />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Amount</Form.Label>
                <Form.Control
                  type="number"
                  value={editingBill.amount}
                  onChange={(e) =>
                    setEditingBill({
                      ...editingBill,
                      amount: parseFloat(e.target.value),
                    })
                  }
                />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Due Day</Form.Label>
                <Form.Control
                  type="number"
                  value={editingBill.due_day}
                  onChange={(e) =>
                    setEditingBill({
                      ...editingBill,
                      due_day: parseInt(e.target.value),
                    })
                  }
                />
              </Form.Group>
              <Form.Group className="mb-3">
                <Form.Label>Class</Form.Label>
                <Form.Control
                  type="text"
                  value={editingBill.bill_class}
                  onChange={(e) =>
                    setEditingBill({
                      ...editingBill,
                      bill_class: e.target.value,
                    })
                  }
                />
              </Form.Group>
            </Form>
          </Modal.Body>
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseModal}>
              Close
            </Button>
            <Button variant="primary" onClick={handleUpdate}>
              Save Changes
            </Button>
          </Modal.Footer>
        </Modal>
      )}
    </div>
  );
};

export default Bills;