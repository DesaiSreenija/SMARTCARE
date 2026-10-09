
import pandas as pd

from src.trend_service import summarize_trend, generate_health_insight


def test_trend_summary():
    measurements = pd.DataFrame({
        "measurement_type": ["heart_rate"] * 3,
        "value": [70, 75, 80],
        "unit": ["bpm"] * 3,
        "recorded_at": [
            "2026-10-01",
            "2026-10-02",
            "2026-10-03",
        ],
    })

    result = summarize_trend(measurements)

    assert result["count"] == 3
    assert result["earliest"] == 70
    assert result["latest"] == 80
    assert result["change"] == 10
    assert result["minimum"] == 70
    assert result["maximum"] == 80
    assert result["average"] == 75


def test_empty_trend_returns_none():
    measurements = pd.DataFrame(
        columns=[
            "measurement_type",
            "value",
            "unit",
            "recorded_at",
        ]
    )

    assert summarize_trend(measurements) is None


def test_health_insight_contains_summary():
    measurements = pd.DataFrame({
        "measurement_type": ["heart_rate"] * 2,
        "value": [70, 80],
        "unit": ["bpm", "bpm"],
        "recorded_at": ["2026-10-01", "2026-10-02"],
    })

    result = generate_health_insight(measurements)

    assert result["status"] == "Descriptive insight"
    assert result["latest"] == 80
    assert result["change"] == 10
    assert "not a diagnosis" in result["message"].lower()
