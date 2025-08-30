import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";
import { API } from "../api/client";
import { Calendar as BigCalendar, momentLocalizer } from "react-big-calendar";
import moment from "moment";
import "react-big-calendar/lib/css/react-big-calendar.css";

const localizer = momentLocalizer(moment);

const Calendar = () => {
  const [events, setEvents] = useState([]); // raw API events
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showBills, setShowBills] = useState(true);
  const [showPayPeriods, setShowPayPeriods] = useState(true);
  const [unpaidOnly, setUnpaidOnly] = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get(API("/calendar"));
        setEvents(res.data || []);
      } catch (e) {
        console.error("Failed to load calendar:", e);
        setError("Failed to load calendar events. Is the backend running?");
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const colorFor = (ev) => {
    if (ev.type === "bill") {
      switch (ev.bill_class) {
        case "Debt":
          return "#c0392b";
        case "Critical":
          return "#e74c3c";
        case "Needed":
          return "#f1c40f";
        case "Comfort":
          return "#3498db";
        case "Essential":
          return "#e67e22";
        default:
          return ev.color || "#95a5a6";
      }
    }
    return ev.color || "#2ecc71";
  };

  const calendarEvents = useMemo(() => {
    return (events || [])
      .filter((ev) => (ev.type === "bill" ? showBills : showPayPeriods))
      .filter((ev) => (unpaidOnly && ev.type === "bill" ? !ev.paid : true))
      .map((ev) => {
        const isBill = ev.type === "bill";
        const start = isBill ? new Date(ev.date) : new Date(ev.start_date);
        const end = isBill ? new Date(ev.date) : new Date(ev.end_date);
        return {
          ...ev,
          start,
          end,
          allDay: !isBill,
          bgColor: colorFor(ev),
          title: isBill
            ? `${ev.title} — $${
                typeof ev.amount === "number" ? ev.amount.toFixed(2) : ev.amount
              }`
            : ev.title,
        };
      });
  }, [events, showBills, showPayPeriods, unpaidOnly]);

  const refresh = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await axios.get(API("/calendar"));
      setEvents(res.data || []);
    } catch (e) {
      setError("Failed to load calendar events.");
    } finally {
      setLoading(false);
    }
  };

  const toggleBillPaid = async (ev) => {
    if (!ev || ev.type !== "bill") return;
    const id = String(ev.id || "").replace("bill-", "");
    const billId = parseInt(id, 10);
    if (!billId) return;
    try {
      await axios.put(API(`/bills/${billId}`), { paid: !ev.paid });
      await refresh();
    } catch (e) {
      alert("Failed to update bill status.");
    }
  };

  return (
    <div>
      <header className="mb-4">
        <h2>Calendar</h2>
        <p className="text-muted mb-0">Upcoming bills and pay periods.</p>
      </header>

      {loading && <div>Loading…</div>}
      {error && <div className="alert alert-danger">{error}</div>}

      {!loading && !error && (
        <>
          <div className="d-flex flex-wrap align-items-center gap-3 mb-2">
            <div className="form-check form-check-inline">
              <input
                className="form-check-input"
                type="checkbox"
                id="fltBills"
                checked={showBills}
                onChange={(e) => setShowBills(e.target.checked)}
              />
              <label className="form-check-label" htmlFor="fltBills">
                Bills
              </label>
            </div>
            <div className="form-check form-check-inline">
              <input
                className="form-check-input"
                type="checkbox"
                id="fltPP"
                checked={showPayPeriods}
                onChange={(e) => setShowPayPeriods(e.target.checked)}
              />
              <label className="form-check-label" htmlFor="fltPP">
                Pay Periods
              </label>
            </div>
            <div className="form-check form-check-inline">
              <input
                className="form-check-input"
                type="checkbox"
                id="fltUnpaid"
                checked={unpaidOnly}
                onChange={(e) => setUnpaidOnly(e.target.checked)}
              />
              <label className="form-check-label" htmlFor="fltUnpaid">
                Unpaid only
              </label>
            </div>
            <div className="ms-auto small text-muted">
              Legend:
              <span
                className="ms-2 me-2"
                style={{
                  display: "inline-block",
                  width: 10,
                  height: 10,
                  background: "#c0392b",
                }}
              ></span>
              Debt
              <span
                className="ms-3 me-2"
                style={{
                  display: "inline-block",
                  width: 10,
                  height: 10,
                  background: "#e74c3c",
                }}
              ></span>
              Critical
              <span
                className="ms-3 me-2"
                style={{
                  display: "inline-block",
                  width: 10,
                  height: 10,
                  background: "#f1c40f",
                }}
              ></span>
              Needed
              <span
                className="ms-3 me-2"
                style={{
                  display: "inline-block",
                  width: 10,
                  height: 10,
                  background: "#3498db",
                }}
              ></span>
              Comfort
              <span
                className="ms-3 me-2"
                style={{
                  display: "inline-block",
                  width: 10,
                  height: 10,
                  background: "#e67e22",
                }}
              ></span>
              Essential
            </div>
          </div>

          <div style={{ height: 500 }}>
            <BigCalendar
              localizer={localizer}
              events={calendarEvents}
              startAccessor="start"
              endAccessor="end"
              style={{ height: 500 }}
              eventPropGetter={(event) => ({
                style: {
                  backgroundColor: event.bgColor,
                  borderColor: event.bgColor,
                  color: "#000",
                },
              })}
              onDoubleClickEvent={(ev) => toggleBillPaid(ev)}
            />
          </div>
        </>
      )}
    </div>
  );
};

export default Calendar;
