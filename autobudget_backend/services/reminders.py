from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from autobudget_backend.db import SessionLocal
from autobudget_backend import models


def _pp_month_key(pp: int) -> str:
    # Duplicate of logic in app._pp_month_key to avoid circular imports
    anchor_pp = 17
    anchor = date(2025, 8, 4)
    delta_weeks = (pp - anchor_pp) * 2
    d = anchor + timedelta(weeks=delta_weeks)
    return f"{d.year}-{d.month:02d}"


def _last_day_of_month(y: int, m: int) -> int:
    nm = 1 if m == 12 else m + 1
    ny = y + 1 if m == 12 else y
    return (date(ny, nm, 1) - timedelta(days=1)).day


def _bill_due_date(bill: models.Bill) -> date:
    ym = _pp_month_key(bill.pp)
    y, m = map(int, ym.split("-"))
    d = min(int(bill.due_day or 1), _last_day_of_month(y, m))
    return date(y, m, d)


def _send_reminder(bill: models.Bill, reminder_type: str) -> None:
    # Placeholder for actual delivery (email/SMS/push). For now, just print.
    print(f"[REMINDER] {reminder_type}: {bill.name} is due soon (${bill.amount:.2f}).")


def send_due_bill_reminders(days_ahead: int = 3) -> int:
    """Find unpaid bills due within days_ahead and send unique reminders.

    Duplicate prevention: for a (bill_id, reminder_type) pair, if a reminder
    exists with sent_at within the last 24h, we skip sending another.

    Returns the number of reminders sent.
    """
    db: Session = SessionLocal()
    sent_count = 0
    try:
        today = date.today()
        window_end = today + timedelta(days=days_ahead)
        unpaid: List[models.Bill] = (
            db.query(models.Bill)
            .filter(models.Bill.paid == False)
            .all()
        )

        now = datetime.utcnow()
        for b in unpaid:
            due = _bill_due_date(b)
            if today <= due <= window_end:
                reminder_type = "due_in_3_days" if (due - today).days <= 3 else "due_soon"

                # Check last reminder within 24 hours
                recent = (
                    db.query(models.Reminder)
                    .filter(models.Reminder.bill_id == b.id)
                    .filter(models.Reminder.reminder_type == reminder_type)
                    .order_by(models.Reminder.sent_at.desc())
                    .first()
                )
                if recent and (now - recent.sent_at).total_seconds() < 24 * 3600:
                    continue  # skip duplicate within 24h

                _send_reminder(b, reminder_type)
                rec = models.Reminder(
                    bill_id=b.id,
                    sent_at=now,
                    reminder_type=reminder_type,
                )
                db.add(rec)
                sent_count += 1

        db.commit()
        return sent_count
    finally:
        db.close()
