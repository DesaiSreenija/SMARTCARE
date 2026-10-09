
from datetime import date, timedelta

from src.database import get_connection, initialize_database


def seed_database():
    """Create synthetic SmartCare AI data without duplicating records."""

    initialize_database()
    today = date.today()

    patients = [
        ("P001", "Alex Morgan", 35, "Not specified"),
        ("P002", "Jamie Taylor", 48, "Not specified"),
        ("P003", "Sam Jordan", 27, "Not specified"),
    ]

    # Synthetic measurements for demonstration only.
    # These values are not real patient data or clinical recommendations.
    synthetic_measurements = {
        "P001": {
            "heart_rate": (
                [72, 74, 76, 75, 78, 77, 79], "bpm"
            ),
            "body_temperature": (
                [36.6, 36.7, 36.8, 36.7, 36.9, 36.8, 36.7],
                "°C",
            ),
            "oxygen_saturation": (
                [98, 98, 97, 98, 97, 98, 98], "%",
            ),
        },
        "P002": {
            "heart_rate": (
                [75, 76, 78, 77, 79, 80, 78], "bpm"
            ),
            "body_temperature": (
                [36.7, 36.8, 36.7, 36.9, 36.8, 36.7, 36.8],
                "°C",
            ),
            "oxygen_saturation": (
                [97, 98, 98, 97, 98, 97, 98], "%",
            ),
        },
        "P003": {
            "heart_rate": (
                [68, 70, 71, 69, 72, 70, 71], "bpm"
            ),
            "body_temperature": (
                [36.5, 36.6, 36.6, 36.7, 36.6, 36.5, 36.6],
                "°C",
            ),
            "oxygen_saturation": (
                [99, 98, 99, 98, 99, 98, 99], "%",
            ),
        },
    }

    with get_connection() as conn:

        # 1. Insert patients if they do not already exist.
        for patient in patients:
            conn.execute(
                """
                INSERT OR IGNORE INTO patients
                    (patient_id, display_name, age, sex)
                VALUES (?, ?, ?, ?)
                """,
                patient,
            )

        # 2. Insert sample medications if missing.
        medications = [
            ("P001", "Sample Medication A", "As prescribed", "08:00"),
            ("P001", "Sample Medication B", "As prescribed", "20:00"),
            ("P002", "Sample Medication C", "As prescribed", "09:00"),
            ("P003", "Sample Medication D", "As prescribed", "08:00"),
        ]

        for patient_id, name, dosage, schedule in medications:
            exists = conn.execute(
                """
                SELECT COUNT(*) FROM medications
                WHERE patient_id = ? AND medication_name = ?
                """,
                (patient_id, name),
            ).fetchone()[0]

            if not exists:
                conn.execute(
                    """
                    INSERT INTO medications
                        (patient_id, medication_name, dosage, schedule)
                    VALUES (?, ?, ?, ?)
                    """,
                    (patient_id, name, dosage, schedule),
                )

        # 3. Insert sample allergies if missing.
        allergies = [
            ("P001", "Sample Allergen A", "Sample reaction"),
            ("P002", "Sample Allergen B", "Sample reaction"),
        ]

        for patient_id, allergen, reaction in allergies:
            exists = conn.execute(
                """
                SELECT COUNT(*) FROM allergies
                WHERE patient_id = ? AND allergen = ?
                """,
                (patient_id, allergen),
            ).fetchone()[0]

            if not exists:
                conn.execute(
                    """
                    INSERT INTO allergies
                        (patient_id, allergen, reaction)
                    VALUES (?, ?, ?)
                    """,
                    (patient_id, allergen, reaction),
                )

        # 4. Replace old placeholder measurements with meaningful
        # synthetic measurement types.
        #
        # Preserve existing meaningful measurements. Only remove
        # the old placeholder type for these sample patients.
        for patient_id in synthetic_measurements:
            conn.execute(
                """
                DELETE FROM measurements
                WHERE patient_id = ?
                  AND measurement_type = 'sample_measurement'
                """,
                (patient_id,),
            )

        for patient_id, measurement_types in synthetic_measurements.items():
            for measurement_type, (values, unit) in (
                measurement_types.items()
            ):

                # Do not insert the same measurement series twice.
                exists = conn.execute(
                    """
                    SELECT COUNT(*) FROM measurements
                    WHERE patient_id = ?
                      AND measurement_type = ?
                    """,
                    (patient_id, measurement_type),
                ).fetchone()[0]

                if exists:
                    print(
                        f"Measurements already exist: "
                        f"{patient_id} - {measurement_type}"
                    )
                    continue

                for day, value in enumerate(values):
                    recorded_date = (
                        today - timedelta(days=6 - day)
                    ).isoformat()

                    conn.execute(
                        """
                        INSERT INTO measurements
                            (patient_id, measurement_type, value,
                             unit, recorded_at)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            patient_id,
                            measurement_type,
                            value,
                            unit,
                            recorded_date,
                        ),
                    )

        # 5. Insert sample appointments if missing.
        appointments = [
            (
                "P001",
                (today + timedelta(days=2)).isoformat(),
                "General Medicine",
                "Scheduled",
            ),
            (
                "P002",
                (today + timedelta(days=5)).isoformat(),
                "General Medicine",
                "Scheduled",
            ),
        ]

        for patient_id, appointment_date, specialty, status in appointments:
            exists = conn.execute(
                """
                SELECT COUNT(*) FROM appointments
                WHERE patient_id = ?
                  AND appointment_date = ?
                  AND specialty = ?
                """,
                (patient_id, appointment_date, specialty),
            ).fetchone()[0]

            if not exists:
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

    print("SmartCare AI synthetic data setup completed.")


if __name__ == "__main__":
    seed_database()
