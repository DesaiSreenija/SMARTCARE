
from src.database import get_connection


def get_patients():
    """Return all registered patients."""

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT patient_id, display_name, age, sex
            FROM patients
            ORDER BY patient_id
            """
        ).fetchall()

    return [dict(row) for row in rows]


def add_patient(display_name, age, sex):
    """Register a patient and return their new patient ID."""

    display_name = display_name.strip()
    sex = sex.strip()

    if not display_name:
        raise ValueError("Patient name is required.")

    if not isinstance(age, int) or not 1 <= age <= 120:
        raise ValueError("Age must be between 1 and 120.")

    with get_connection() as conn:
        # Generate the next available ID, such as P004.
        rows = conn.execute(
            "SELECT patient_id FROM patients"
        ).fetchall()

        numbers = []

        for row in rows:
            patient_id = row["patient_id"]

            if (
                isinstance(patient_id, str)
                and patient_id.startswith("P")
                and patient_id[1:].isdigit()
            ):
                numbers.append(int(patient_id[1:]))

        next_number = max(numbers, default=0) + 1

        # Skip an ID if it already exists.
        while True:
            new_id = f"P{next_number:03d}"

            exists = conn.execute(
                "SELECT 1 FROM patients WHERE patient_id = ?",
                (new_id,),
            ).fetchone()

            if exists is None:
                break

            next_number += 1

        conn.execute(
            """
            INSERT INTO patients
                (patient_id, display_name, age, sex)
            VALUES (?, ?, ?, ?)
            """,
            (new_id, display_name, age, sex),
        )

    return new_id
