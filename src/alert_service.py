
from src.trend_service import get_measurements


# Demonstration thresholds only.
# Validate thresholds against appropriate clinical sources before
# using this system for any real patient-care purpose.
DEMO_THRESHOLDS = {
    "heart_rate": {
        "unit": "bpm",
        "low": 60,
        "high": 100,
    },
    "body_temperature": {
        "unit": "°C",
        "low": 35.0,
        "high": 38.0,
    },
    "oxygen_saturation": {
        "unit": "%",
        "low": 95,
        "high": 100,
    },
}


def evaluate_measurement(measurement_type, value, unit):
    """Evaluate one measurement using configured demo thresholds."""

    if value is None:
        return {
            "status": "Unassessed",
            "message": "No measurement value is available.",
        }

    try:
        value = float(value)
    except (TypeError, ValueError):
        return {
            "status": "Unassessed",
            "message": "The measurement value is invalid.",
        }

    rule = DEMO_THRESHOLDS.get(measurement_type)

    if rule is None:
        return {
            "status": "Unassessed",
            "message": "No demonstration rule is configured for this measurement.",
        }

    if unit != rule["unit"]:
        return {
            "status": "Unassessed",
            "message": (
                f"Expected unit {rule['unit']}; received {unit}. "
                "The measurement was not assessed."
            ),
        }

    if measurement_type == "oxygen_saturation" and not 0 <= value <= 100:
        return {
            "status": "Unassessed",
            "message": "The oxygen saturation value is outside the valid percentage range.",
        }

    if value < rule["low"]:
        return {
            "status": "Review",
            "message": (
                f"{measurement_type} is below the configured "
                f"demonstration threshold ({rule['low']} {unit})."
            ),
        }

    if value > rule["high"]:
        return {
            "status": "Review",
            "message": (
                f"{measurement_type} is above the configured "
                f"demonstration threshold ({rule['high']} {unit})."
            ),
        }

    return {
        "status": "Within demo thresholds",
        "message": (
            "The measurement is within the configured demonstration "
            "thresholds. This does not guarantee that it is medically normal."
        ),
    }


def get_patient_alerts(patient_id):
    """Assess the latest available measurement of each configured type."""

    measurements = get_measurements(patient_id)

    if measurements.empty:
        return []

    measurements = measurements.copy()
    measurements["recorded_at"] = measurements["recorded_at"].astype(str)

    latest_rows = (
        measurements.sort_values("recorded_at")
        .groupby("measurement_type", sort=False)
        .tail(1)
    )

    alerts = []

    for _, row in latest_rows.iterrows():
        result = evaluate_measurement(
            row["measurement_type"],
            row["value"],
            row["unit"],
        )

        alerts.append({
            "measurement_type": row["measurement_type"],
            "value": row["value"],
            "unit": row["unit"],
            "recorded_at": row["recorded_at"],
            **result,
        })

    return alerts
