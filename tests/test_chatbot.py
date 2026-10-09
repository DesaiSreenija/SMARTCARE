
from src.nlp_engine import load_model, predict_intent


def test_supported_medication_question():
    model = load_model()

    intent, confidence = predict_intent(
        model, "Show my medications"
    )

    assert intent == "view_medications"
    assert 0 <= confidence <= 1


def test_supported_schedule_question():
    model = load_model()

    intent, confidence = predict_intent(
        model, "What is my medication schedule?"
    )

    assert intent == "medication_schedule"
    assert 0 <= confidence <= 1


def test_supported_allergy_question():
    model = load_model()

    intent, confidence = predict_intent(
        model, "Show my recorded allergies"
    )

    assert intent == "view_allergies"
    assert 0 <= confidence <= 1


def test_supported_appointment_question():
    model = load_model()

    intent, confidence = predict_intent(
        model, "When is my next appointment?"
    )

    assert intent == "view_appointments"
    assert 0 <= confidence <= 1


def test_supported_health_trend_question():
    model = load_model()

    intent, confidence = predict_intent(
        model, "Show my measurement history"
    )

    assert intent == "summarize_health_trends"
    assert 0 <= confidence <= 1


def test_unrelated_question_is_rejected():
    model = load_model()

    intent, confidence = predict_intent(
        model, "Write a poem about space"
    )

    assert intent == "unknown"
    assert 0 <= confidence <= 1
