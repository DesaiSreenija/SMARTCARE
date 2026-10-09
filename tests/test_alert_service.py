
from src.alert_service import evaluate_measurement


def test_normal_demo_heart_rate():
    result = evaluate_measurement("heart_rate", 79, "bpm")
    assert result["status"] == "Within demo thresholds"


def test_low_demo_heart_rate_is_flagged():
    result = evaluate_measurement("heart_rate", 50, "bpm")
    assert result["status"] == "Review"


def test_unknown_measurement_is_not_assessed():
    result = evaluate_measurement("unknown_type", 10, "units")
    assert result["status"] == "Unassessed"


def test_wrong_unit_is_not_assessed():
    result = evaluate_measurement("heart_rate", 79, "°C")
    assert result["status"] == "Unassessed"


def test_invalid_value_is_not_assessed():
    result = evaluate_measurement("heart_rate", "invalid", "bpm")
    assert result["status"] == "Unassessed"
