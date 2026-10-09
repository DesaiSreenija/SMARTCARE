
import pandas as pd

from src.database import get_connection


def get_measurements(patient_id, measurement_type=None):
    """Fetch measurement history for a selected patient."""

    query = """
        SELECT measurement_type, value, unit, recorded_at
        FROM measurements
        WHERE patient_id = ?
    """
    params = [patient_id]

    if measurement_type is not None:
        query += " AND measurement_type = ?"
        params.append(measurement_type)

    query += " ORDER BY recorded_at"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    df = pd.DataFrame(
        [dict(row) for row in rows],
        columns=[
            "measurement_type",
            "value",
            "unit",
            "recorded_at"
        ]
    )

    if not df.empty:
        df["value"] = pd.to_numeric(df["value"], errors="coerce")
        df = df.dropna(subset=["value"])

    return df


def summarize_trend(measurements):
    """Calculate descriptive statistics for a measurement series."""

    if measurements.empty:
        return None

    values = pd.to_numeric(
        measurements["value"], errors="coerce"
    ).dropna()

    if values.empty:
        return None

    return {
        "count": int(len(values)),
        "latest": float(values.iloc[-1]),
        "earliest": float(values.iloc[0]),
        "change": float(values.iloc[-1] - values.iloc[0]),
        "minimum": float(values.min()),
        "maximum": float(values.max()),
        "average": float(values.mean())
    }


def generate_health_insight(measurements):
    """
    Generate a descriptive insight for one measurement series.
    This function does not diagnose medical conditions.
    """

    summary = summarize_trend(measurements)

    if summary is None:
        return {
            "status": "No data",
            "message": "No valid measurements are available."
        }

    measurement_type = str(
        measurements["measurement_type"].iloc[0]
    )
    unit = str(measurements["unit"].iloc[-1])

    change = summary["change"]

    if change > 0:
        direction = "increased"
    elif change < 0:
        direction = "decreased"
    else:
        direction = "remained unchanged"

    return {
        "status": "Descriptive insight",
        "measurement_type": measurement_type,
        "count": summary["count"],
        "earliest": summary["earliest"],
        "latest": summary["latest"],
        "change": change,
        "minimum": summary["minimum"],
        "maximum": summary["maximum"],
        "average": summary["average"],
        "unit": unit,
        "message": (
            f"{measurement_type} {direction} by "
            f"{abs(change):.2f} {unit} across the recorded "
            f"measurements. The latest value is "
            f"{summary['latest']:.2f} {unit}. "
            "This is a descriptive summary, not a diagnosis."
        )
    }
