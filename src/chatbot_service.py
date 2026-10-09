
from src.database import get_connection
from src.nlp_engine import load_model, predict_intent


def answer_question(patient_id, question):
    model = load_model()
    intent, confidence = predict_intent(model, question)

    if intent == "unknown":
        return {
            "intent": intent,
            "confidence": confidence,
            "answer": (
                "I'm not confident enough to interpret that question. "
                "Please rephrase it or select a supported question."
            )
        }

    with get_connection() as conn:

        if intent == "view_medications":
            rows = conn.execute(
                """
                SELECT medication_name, dosage, schedule
                FROM medications
                WHERE patient_id = ?
                ORDER BY medication_name
                """,
                (patient_id,)
            ).fetchall()

            if not rows:
                answer = "No medication records are available."
            else:
                answer = "Recorded medications:\n" + "\n".join(
                    f"- {r['medication_name']}: "
                    f"{r['dosage']}; schedule {r['schedule']}"
                    for r in rows
                )

        elif intent == "medication_schedule":
            rows = conn.execute(
                """
                SELECT medication_name, schedule
                FROM medications
                WHERE patient_id = ?
                ORDER BY schedule
                """,
                (patient_id,)
            ).fetchall()

            answer = (
                "Recorded medication schedules:\n"
                + "\n".join(
                    f"- {r['medication_name']}: {r['schedule']}"
                    for r in rows
                )
                if rows else "No medication schedules are recorded."
            )

        elif intent == "view_allergies":
            rows = conn.execute(
                """
                SELECT allergen, reaction
                FROM allergies
                WHERE patient_id = ?
                """,
                (patient_id,)
            ).fetchall()

            answer = (
                "Recorded allergies:\n"
                + "\n".join(
                    f"- {r['allergen']}: {r['reaction'] or 'Reaction not recorded'}"
                    for r in rows
                )
                if rows else "No allergy information is recorded."
            )

        elif intent == "view_appointments":
            rows = conn.execute(
                """
                SELECT appointment_date, specialty, status
                FROM appointments
                WHERE patient_id = ?
                ORDER BY appointment_date
                """,
                (patient_id,)
            ).fetchall()

            answer = (
                "Recorded appointments:\n"
                + "\n".join(
                    f"- {r['appointment_date']}: "
                    f"{r['specialty']} ({r['status']})"
                    for r in rows
                )
                if rows else "No appointments are recorded."
            )

        elif intent == "summarize_health_trends":
            rows = conn.execute(
                """
                SELECT measurement_type, value, unit, recorded_at
                FROM measurements
                WHERE patient_id = ?
                ORDER BY recorded_at
                """,
                (patient_id,)
            ).fetchall()

            if not rows:
                answer = "No health measurements are recorded."
            else:
                values = [float(r["value"]) for r in rows]
                latest = rows[-1]

                answer = (
                    f"Recorded measurements: {len(rows)}\n"
                    f"Latest entry: {latest['measurement_type']} = "
                    f"{latest['value']} {latest['unit']} "
                    f"on {latest['recorded_at']}\n"
                    f"Earliest-to-latest numerical change: "
                    f"{values[-1] - values[0]:+.2f}\n"
                    "These are descriptive statistics, not a diagnosis."
                )

        else:
            answer = (
                "I cannot answer that question using the available records."
            )

    return {
        "intent": intent,
        "confidence": confidence,
        "answer": answer
    }
