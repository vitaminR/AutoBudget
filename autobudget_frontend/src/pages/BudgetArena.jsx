import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API } from '../api/client';

const BudgetArena = () => {
  const [status, setStatus] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = () => {
    setLoading(true);
    axios.all([
      axios.get(API('/gamification/status')),
      axios.get(API('/gamification/tasks')),
    ])
    .then(axios.spread((statusRes, tasksRes) => {
      setStatus(statusRes.data);
      setTasks(tasksRes.data);
    }))
    .catch(err => {
      console.error("Error fetching game data:", err);
      setError('Failed to load game data.');
    })
    .finally(() => {
      setLoading(false);
    });
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCompleteTask = (playerId, task) => {
    // First, award the points for the gamification task
    axios.post(API('/gamification/complete-task'), { player_id: playerId, task_type: task.task_type })
      .then(() => {
        // Then, mark the actual bill as paid
        return axios.post(API(`/bills/${task.id}/toggle-paid`));
      })
      .then(() => {
        // Refresh all data after both actions are successful
        fetchData();
      })
      .catch(err => {
        console.error(`Error completing task ${task.name} for ${playerId}:`, err);
        setError('Failed to update task. Please try again.');
      });
  };

  const PlayerCard = ({ player, playerId }) => {
    if (!player) return null;

    return (
      <div className="card h-100">
        <div className="card-body">
          <h5 className="card-title text-capitalize">{playerId}</h5>
          <p className="card-text fs-4">{player.points} <span className="text-muted fs-6">Points</span></p>
          <p className="card-text fs-4">${player.spending_money.toFixed(2)} <span className="text-muted fs-6">Spending Money</span></p>
        </div>
      </div>
    );
  };

  return (
    <div>
      <header className="mb-4">
        <h2>Budget Arena</h2>
        <p className="text-muted">Complete financial tasks to earn points and unlock spending money. First come, first served!</p>
      </header>

      {loading && <p>Loading game status...</p>}
      {error && <div className="alert alert-danger">{error}</div>}

      {status && (
        <div className="row">
          <div className="col-md-6 mb-4">
            <PlayerCard player={status.player1} playerId="player1" />
          </div>
          <div className="col-md-6 mb-4">
            <PlayerCard player={status.player2} playerId="player2" />
          </div>
        </div>
      )}

      <div className="card">
        <div className="card-header">
          <h5>Task Board (Unpaid Bills)</h5>
        </div>
        <div className="card-body">
          {tasks.length > 0 ? (
            <ul className="list-group list-group-flush">
              {tasks.map(task => (
                <li key={task.id} className="list-group-item d-flex justify-content-between align-items-center">
                  <div>
                    <strong>{task.name}</strong> (${task.amount.toFixed(2)})
                    <br />
                    <small className="text-muted">Category: {task.bill_class}</small>
                  </div>
                  <div className="btn-group">
                    <button className="btn btn-sm btn-success" onClick={() => handleCompleteTask('player1', task)}>P1 Completes</button>
                    <button className="btn btn-sm btn-info" onClick={() => handleCompleteTask('player2', task)}>P2 Completes</button>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-muted">No available tasks. All bills are paid!</p>
          )}
        </div>
      </div>

    </div>
  );
};

export default BudgetArena;