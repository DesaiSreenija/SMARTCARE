
import sqlite3

import pytest

from src import patient_service


@pytest.fixture
def temporary_database(monkeypatch):
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    connection.execute("""
        CREATE TABLE patients (
            patient_id TEXT PRIMARY KEY,
            display_name TEXT,
            age INTEGER,
            sex TEXT
        )
    """)

    connection.executemany(
        """
        INSERT INTO patients
            (patient_id, display_name, age, sex)
        VALUES (?, ?, ?, ?)
        """,
        [
            ("P001", "Alex Morgan", 35, "Not specified"),
            ("P003", "Sam Jordan", 27, "Not specified"),
        ],
    )

    class ConnectionContext:
        def __enter__(self):
            return connection

        def __exit__(self, exc_type, exc, tb):
            if exc_type is not None:
                connection.rollback()
            else:
                connection.commit()
            return False

    monkeypatch.setattr(
        patient_service,
        "get_connection",
        lambda: ConnectionContext(),
    )

    yield connection
    connection.close()


def test_add_patient_generates_unique_id(temporary_database):
    patient_id = patient_service.add_patient(
        "Taylor Reed", 30, "Not specified"
    )

    assert patient_id == "P004"

    row = temporary_database.execute(
        "SELECT * FROM patients WHERE patient_id = ?",
        (patient_id,),
    ).fetchone()

    assert row["display_name"] == "Taylor Reed"
    assert row["age"] == 30


def test_patient_list_includes_new_patient(temporary_database):
    patient_service.add_patient(
        "Taylor Reed", 30, "Not specified"
    )

    patients = patient_service.get_patients()

    assert any(
        patient["display_name"] == "Taylor Reed"
        for patient in patients
    )


def test_reject_blank_patient_name(temporary_database):
    with pytest.raises(ValueError):
        patient_service.add_patient(
            "   ", 30, "Not specified"
        )


def test_reject_invalid_age(temporary_database):
    with pytest.raises(ValueError):
        patient_service.add_patient(
            "Taylor Reed", 0, "Not specified"
        )
