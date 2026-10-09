
from multiprocessing import connection
import sqlite3
from pathlib import Path

# Store the database inside the project folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "smartcare.db"


def get_connection():
    """Create a connection to the SQLite database."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    """Create the tables required by SmartCare AI."""

    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                age INTEGER,
                sex TEXT
            );
            
            
            CREATE TABLE IF NOT EXISTS adherence_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                medication_id INTEGER NOT NULL,
                scheduled_at TEXT NOT NULL,
                status TEXT NOT NULL
                    CHECK (status IN ('Taken', 'Skipped')),
                recorded_at TEXT NOT NULL,
                FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
                FOREIGN KEY (medication_id) REFERENCES medications(medication_id)
            );


            CREATE TABLE IF NOT EXISTS medications (
                medication_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                medication_name TEXT NOT NULL,
                dosage TEXT NOT NULL,
                schedule TEXT NOT NULL,
                FOREIGN KEY (patient_id)
                    REFERENCES patients(patient_id)
            );

            CREATE TABLE IF NOT EXISTS allergies (
                allergy_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                allergen TEXT NOT NULL,
                reaction TEXT,
                FOREIGN KEY (patient_id)
                    REFERENCES patients(patient_id)
            );

            CREATE TABLE IF NOT EXISTS measurements (
                measurement_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                measurement_type TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                FOREIGN KEY (patient_id)
                    REFERENCES patients(patient_id)
            );

            CREATE TABLE IF NOT EXISTS appointments (
                appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                appointment_date TEXT NOT NULL,
                specialty TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (patient_id)
                    REFERENCES patients(patient_id)
            );

            CREATE TABLE IF NOT EXISTS adherence_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                medication_id INTEGER NOT NULL,
                scheduled_at TEXT NOT NULL,
                status TEXT NOT NULL,
                recorded_at TEXT NOT NULL,
                FOREIGN KEY (patient_id)
                    REFERENCES patients(patient_id),
                FOREIGN KEY (medication_id)
                    REFERENCES medications(medication_id)
            );
        """)

        # Enable SQLite foreign-key enforcement.
        conn.execute("PRAGMA foreign_keys = ON")
        # connection.execute("PRAGMA foreign_keys = ON")


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized at: {DB_PATH}")
