
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


def add_medication(patient_id, medication_name, dosage, schedule):
    """Add a medication record for an existing patient."""
    medication_name = medication_name.strip()
    dosage = dosage.strip()
    schedule = schedule.strip()

    if not medication_name or not dosage or not schedule:
        raise ValueError("Medication name, dosage, and schedule are required.")

    with get_connection() as conn:
        patient = conn.execute(
            "SELECT patient_id FROM patients WHERE patient_id = ?",
            (patient_id,)
        ).fetchone()

        if not patient:
            raise ValueError("Patient does not exist.")

        conn.execute(
            """
            INSERT INTO medications
                (patient_id, medication_name, dosage, schedule)
            VALUES (?, ?, ?, ?)
            """,
            (patient_id, medication_name, dosage, schedule)
        )

        conn.commit()


def add_allergy(patient_id, allergen, reaction=""):
    """Add an allergy record for an existing patient."""
    allergen = allergen.strip()
    reaction = reaction.strip()

    if not allergen:
        raise ValueError("Allergen is required.")

    with get_connection() as conn:
        patient = conn.execute(
            "SELECT patient_id FROM patients WHERE patient_id = ?",
            (patient_id,)
        ).fetchone()

        if not patient:
            raise ValueError("Patient does not exist.")

        conn.execute(
            """
            INSERT INTO allergies (patient_id, allergen, reaction)
            VALUES (?, ?, ?)
            """,
            (patient_id, allergen, reaction or None)
        )

        conn.commit()
