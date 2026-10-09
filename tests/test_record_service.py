
import sqlite3

import pytest

from src import record_service


@pytest.fixture
def temporary_database(monkeypatch):
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    connection.executescript("""
        CREATE TABLE patients (
            patient_id TEXT PRIMARY KEY,
            display_name TEXT,
            age INTEGER,
            sex TEXT
        );

        CREATE TABLE measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            measurement_type TEXT,
            value REAL,
            unit TEXT,
            recorded_at TEXT
        );

        CREATE TABLE appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT,
            appointment_date TEXT,
            specialty TEXT,
            status TEXT
        );

        INSERT INTO patients
        VALUES ('P999', 'Test Patient', 30, 'Not specified');
    """)

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
        record_service,
        "get_connection",
        lambda: ConnectionContext()
    )

    yield connection
    connection.close()


def test_add_measurement_and_persist(temporary_database):
    record_service.add_measurement(
        "P999",
        "heart_rate",
        75,
        "bpm",
        "2026-10-09"
    )

    row = temporary_database.execute(
        "SELECT * FROM measurements WHERE patient_id = 'P999'"
    ).fetchone()

    assert row is not None
    assert row["value"] == 75
    assert row["unit"] == "bpm"


def test_reject_unsupported_measurement(temporary_database):
    with pytest.raises(ValueError):
        record_service.add_measurement(
            "P999", "unknown_type", 10, "units"
        )


def test_reject_missing_patient(temporary_database):
    with pytest.raises(ValueError):
        record_service.add_measurement(
            "P404", "heart_rate", 75, "bpm"
        )


def test_add_appointment_and_persist(temporary_database):
    record_service.add_appointment(
        "P999",
        "2026-11-01",
        "General Medicine",
        "Scheduled"
    )

    row = temporary_database.execute(
        "SELECT * FROM appointments WHERE patient_id = 'P999'"
    ).fetchone()

    assert row is not None
    assert row["specialty"] == "General Medicine"
    assert row["status"] == "Scheduled"
