
from datetime import date

from src.database import get_connection


ALLOWED_MEASUREMENTS = {
    "heart_rate": "bpm",
    "body_temperature": "°C",
    "oxygen_saturation": "%",
}


def add_measurement(
    patient_id,
    measurement_type,
    value,
    unit,
    recorded_at=None,
):
    """Save a measurement for an existing patient."""

    if measurement_type not in ALLOWED_MEASUREMENTS:
        raise ValueError("Unsupported measurement type.")

    expected_unit = ALLOWED_MEASUREMENTS[measurement_type]

    if unit != expected_unit:
        raise ValueError(
            f"{measurement_type} must use {expected_unit}."
        )

    try:
        value = float(value)
    except (TypeError, ValueError):
        raise ValueError("Measurement value must be numeric.")

    if value <= 0:
        raise ValueError("Measurement value must be positive.")

    if measurement_type == "oxygen_saturation" and value > 100:
        raise ValueError("Oxygen saturation cannot exceed 100%.")

    if recorded_at is None:
        recorded_at = date.today().isoformat()

    with get_connection() as conn:
        patient = conn.execute(
            "SELECT 1 FROM patients WHERE patient_id = ?",
            (patient_id,),
        ).fetchone()

        if patient is None:
            raise ValueError("Selected patient does not exist.")

        conn.execute(
            """
            INSERT INTO measurements
                (patient_id, measurement_type, value, unit, recorded_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                patient_id,
                measurement_type,
                value,
                unit,
                recorded_at,
            ),
        )


from datetime import date


def add_appointment(
    patient_id,
    appointment_date,
    specialty,
    status="Scheduled",
):
    """Save an appointment for an existing patient."""

    specialty = specialty.strip()

    if not specialty:
        raise ValueError("Specialty or appointment type is required.")

    if status not in {"Scheduled", "Completed", "Cancelled"}:
        raise ValueError("Invalid appointment status.")

    if isinstance(appointment_date, date):
        appointment_date = appointment_date.isoformat()

    with get_connection() as conn:
        patient = conn.execute(
            "SELECT 1 FROM patients WHERE patient_id = ?",
            (patient_id,),
        ).fetchone()

        if patient is None:
            raise ValueError("Selected patient does not exist.")

        conn.execute(
            """
            INSERT INTO appointments
                (patient_id, appointment_date, specialty, status)
            VALUES (?, ?, ?, ?)
            """,
            (
                patient_id,
                appointment_date,
                specialty,
                status,
            ),
        )
