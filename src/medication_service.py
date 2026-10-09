
from datetime import datetime

from src.database import get_connection


def get_medications(patient_id):
    """Return medications belonging to one patient."""
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT medication_id, medication_name, dosage, schedule
            FROM medications
            WHERE patient_id = ?
            ORDER BY medication_name
            """,
            (patient_id,)
        ).fetchall()


def record_dose(patient_id, medication_id, scheduled_at, status):
    """Record a dose event for a patient's medication."""

    if status not in ("Taken", "Skipped"):
        raise ValueError("Invalid medication event status.")

    with get_connection() as conn:
        medication = conn.execute(
            """
            SELECT medication_id
            FROM medications
            WHERE medication_id = ?
              AND patient_id = ?
            """,
            (medication_id, patient_id)
        ).fetchone()

        if medication is None:
            raise ValueError(
                "Medication does not belong to this patient."
            )

        conn.execute(
            """
            INSERT INTO adherence_events
            (patient_id, medication_id, scheduled_at,
             status, recorded_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                patient_id,
                medication_id,
                scheduled_at,
                status,
                datetime.now().astimezone().isoformat()
            )
        )


def get_adherence_history(patient_id):
    """Return the recorded dose history for one patient."""
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT
                e.event_id,
                m.medication_name,
                e.scheduled_at,
                e.status,
                e.recorded_at
            FROM adherence_events AS e
            JOIN medications AS m
              ON e.medication_id = m.medication_id
            WHERE e.patient_id = ?
            ORDER BY e.scheduled_at DESC
            """,
            (patient_id,)
        ).fetchall()
