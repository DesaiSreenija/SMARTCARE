
import streamlit as st
import pandas as pd

from src.database import get_connection, initialize_database
from src.chatbot_service import answer_question
from datetime import date, datetime, time

from src.alert_service import get_patient_alerts
from src.patient_service import add_patient
from src.record_service import add_measurement
from src.record_service import add_measurement, add_appointment

from src.trend_service import (
    get_measurements,
    summarize_trend,
    generate_health_insight
)

from src.medication_service import (
    get_medications,
    record_dose,
    get_adherence_history,
)

from src.trend_service import (
    get_measurements,
    summarize_trend,
)

st.set_page_config(
    page_title="SmartCare AI",
    page_icon="🏥",
    layout="wide"
)

initialize_database()


# Patient registration
with st.expander("➕ Add New Patient", expanded=False):
    st.subheader("Register a Synthetic Patient")

    with st.form("add_patient_form", clear_on_submit=True):
        new_name = st.text_input(
            "Patient name",
            placeholder="Enter a fictional patient name"
        )

        new_age = st.number_input(
            "Age",
            min_value=1,
            max_value=120,
            value=25,
            step=1
        )

        new_sex = st.selectbox(
            "Sex",
            ["Not specified", "Female", "Male", "Other"]
        )

        add_submitted = st.form_submit_button(
            "Register Patient"
        )

        if add_submitted:
            try:
                new_patient_id = add_patient(
                    new_name,
                    int(new_age),
                    new_sex
                )

                st.session_state["new_patient_id"] = new_patient_id
                st.success(
                    f"Patient registered successfully! "
                    f"Patient ID: {new_patient_id}"
                )

            except ValueError as exc:
                st.error(str(exc))


st.title("🏥 SmartCare AI")
st.caption("Intelligent Personal Health Record Assistant")
st.info(
    "Academic prototype using fictional records. "
    "Not intended for diagnosis or treatment."
)


def load_table(query, params=()):
    with get_connection() as conn:
        return pd.read_sql_query(query, conn, params=params)



patients = load_table("""
    SELECT patient_id, display_name, age
    FROM patients
    ORDER BY patient_id
""")

if patients.empty:
    st.warning(
        "No patients found. Register a patient or run: "
        "python -m src.seed_data"
    )
    st.stop()

patient_ids = patients["patient_id"].tolist()

# Select the newly registered patient after the form submits.
preferred_id = st.session_state.get("new_patient_id")

if preferred_id in patient_ids:
    default_index = patient_ids.index(preferred_id)
else:
    default_index = 0

selected_id = st.selectbox(
    "Select a synthetic patient",
    patient_ids,
    index=default_index,
    format_func=lambda pid: (
        patients.loc[
            patients["patient_id"] == pid, "display_name"
        ].iloc[0] + f" ({pid})"
    ),
    key="selected_patient_id"
)

patient = patients[patients["patient_id"] == selected_id].iloc[0]

st.subheader(f"Welcome, {patient['display_name']}")

medications = load_table("""
    SELECT medication_name, dosage, schedule
    FROM medications
    WHERE patient_id = ?
""", (selected_id,))

allergies = load_table("""
    SELECT allergen, reaction
    FROM allergies
    WHERE patient_id = ?
""", (selected_id,))

measurements = load_table("""
    SELECT measurement_type, value, unit, recorded_at
    FROM measurements
    WHERE patient_id = ?
    ORDER BY recorded_at
""", (selected_id,))

appointments = load_table("""
    SELECT appointment_date, specialty, status
    FROM appointments
    WHERE patient_id = ?
    ORDER BY appointment_date
""", (selected_id,))

col1, col2, col3 = st.columns(3)
col1.metric("Medication records", len(medications))
col2.metric("Recorded allergies", len(allergies))
col3.metric("Measurements", len(measurements))

tab1, tab2, tab3, tab4 = st.tabs([
    "Medications",
    "Allergies",
    "Health Measurements",
    "Appointments"
])


with tab1:
    st.subheader("Medication Records")

    meds = get_medications(selected_id)

    if not meds:
        st.info("No medication records are available.")
    else:
        for med in meds:
            with st.container(border=True):
                st.write(f"**{med['medication_name']}**")
                st.write(f"Schedule: {med['schedule']}")
                st.write(f"Recorded instructions: {med['dosage']}")

        st.divider()
        st.subheader("Record a Dose Event")

        med_options = {
            f"{m['medication_name']} — {m['schedule']}": m
            for m in meds
        }

        with st.form("dose_event_form"):
            selected_med_label = st.selectbox(
                "Medication",
                list(med_options.keys())
            )

            dose_date = st.date_input(
                "Scheduled date",
                value=date.today()
            )

            dose_time = st.time_input(
                "Scheduled time",
                value=time(8, 0)
            )

            dose_status = st.radio(
                "Recorded event",
                ["Taken", "Skipped"],
                horizontal=True
            )

            submitted = st.form_submit_button("Save dose event")

            if submitted:
                selected_med = med_options[selected_med_label]
                scheduled_at = datetime.combine(
                    dose_date, dose_time
                ).isoformat()

                try:
                    record_dose(
                        selected_id,
                        selected_med["medication_id"],
                        scheduled_at,
                        dose_status
                    )
                    st.success("Dose event recorded.")
                except ValueError as exc:
                    st.error(str(exc))

        st.subheader("Adherence History")
        history = get_adherence_history(selected_id)

        if history:
            st.dataframe(
                [dict(row) for row in history],
                use_container_width=True
            )
        else:
            st.info("No dose events have been recorded yet.")


with tab3:
    st.subheader("Health-Trend Analysis")

    measurements = get_measurements(selected_id)

    if measurements.empty:
        st.info("No measurements are available.")
    else:
        measurement_types = sorted(
            measurements["measurement_type"].unique()
        )

        selected_type = st.selectbox(
            "Measurement type",
            measurement_types
        )

        filtered = measurements[
            measurements["measurement_type"] == selected_type
        ].copy()

        filtered["recorded_at"] = pd.to_datetime(
            filtered["recorded_at"]
        )

        filtered = filtered.sort_values("recorded_at")

        summary = summarize_trend(filtered)

        if summary:
            c1, c2, c3 = st.columns(3)
            c1.metric("Latest value", f"{summary['latest']:.2f}")
            c2.metric("Change", f"{summary['change']:+.2f}")
            c3.metric("Average", f"{summary['average']:.2f}")

            st.write(
                f"Minimum: {summary['minimum']:.2f} | "
                f"Maximum: {summary['maximum']:.2f} | "
                f"Records: {summary['count']}"
            )

            chart_data = filtered.set_index("recorded_at")["value"]
            st.line_chart(chart_data)

            st.caption(
                "Descriptive statistics from synthetic data only. "
                "The current sample measurement is not a clinical "
                "measurement and must not be used for medical decisions."
            )

        st.dataframe(filtered, use_container_width=True)
    
    
st.divider()
st.subheader("➕ Add Health Measurement")

measurement_options = {
    "Heart Rate": ("heart_rate", "bpm"),
    "Body Temperature": ("body_temperature", "°C"),
    "Oxygen Saturation": ("oxygen_saturation", "%"),
}

with st.form("add_measurement_form", clear_on_submit=True):
    measurement_label = st.selectbox(
        "Measurement type",
        list(measurement_options.keys()),
    )

    measurement_value = st.number_input(
        "Measurement value",
        min_value=0.1,
        value=70.0,
        step=0.1,
    )

    measurement_date = st.date_input(
        "Recorded date",
        value=date.today(),
        max_value=date.today(),
    )

    submitted_measurement = st.form_submit_button(
        "Save Measurement"
    )

    if submitted_measurement:
        measurement_type, unit = measurement_options[
            measurement_label
        ]

        try:
            add_measurement(
                selected_id,
                measurement_type,
                measurement_value,
                unit,
                measurement_date.isoformat(),
            )
            st.success("Measurement saved successfully.")
            st.rerun()

        except ValueError as exc:
            st.error(str(exc))


with tab2:
    st.subheader("Recorded Allergies")
    if allergies.empty:
        st.info("No allergy information is recorded.")
    else:
        st.dataframe(allergies, use_container_width=True)

with tab4:
    st.subheader("Appointments")
    if appointments.empty:
        st.info("No appointments are recorded.")
    else:
        st.dataframe(appointments, use_container_width=True)
    


st.divider()
st.subheader("➕ Add Appointment")

with st.form("add_appointment_form", clear_on_submit=True):
    appointment_date = st.date_input(
        "Appointment date",
        value=date.today(),
        min_value=date.today(),
    )

    specialty = st.text_input(
        "Specialty or appointment type",
        placeholder="e.g. General Medicine",
    )

    appointment_status = st.selectbox(
        "Status",
        ["Scheduled", "Completed", "Cancelled"],
    )

    submitted_appointment = st.form_submit_button(
        "Save Appointment"
    )

    if submitted_appointment:
        try:
            add_appointment(
                selected_id,
                appointment_date,
                specialty,
                appointment_status,
            )
            st.success("Appointment saved successfully.")
            st.rerun()

        except ValueError as exc:
            st.error(str(exc))



st.subheader("Safety Alerts")

st.caption(
    "Demonstration rules only. These alerts do not diagnose "
    "medical conditions or replace professional medical advice."
)

alerts = get_patient_alerts(selected_id)

if not alerts:
    st.info("No measurement records are available to assess.")
else:
    for alert in alerts:
        st.markdown(f"**{alert['measurement_type'].replace('_', ' ').title()}**")

        st.write(
            f"Latest value: {alert['value']} {alert['unit']}"
        )
        st.caption(f"Recorded on: {alert['recorded_at']}")

        if alert["status"] == "Review":
            st.warning(alert["message"])
        elif alert["status"] == "Within demo thresholds":
            st.success(alert["message"])
        else:
            st.info(alert["message"])

        st.divider()


        
st.subheader("AI Health Insights")

measurements = get_measurements(selected_id)

if measurements.empty:
    st.info("No measurements are available for this patient.")
else:
    for measurement_type, group in measurements.groupby(
        "measurement_type"
    ):
        insight = generate_health_insight(
            group.reset_index(drop=True)
        )

        st.markdown(f"**{measurement_type}**")
        st.write(insight["message"])

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Earliest value",
            f'{insight["earliest"]:.2f} {insight["unit"]}'
        )

        col2.metric(
            "Latest value",
            f'{insight["latest"]:.2f} {insight["unit"]}'
        )

        col3.metric(
            "Change",
            f'{insight["change"]:+.2f} {insight["unit"]}'
        )

        st.caption(
            "Descriptive analysis only; not a medical diagnosis."
        )



st.divider()
st.header("💬 SmartCare AI Assistant")

st.caption(
    "Ask questions about the selected synthetic patient's records."
)

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input(
    "Ask about medications, allergies, appointments, or trends..."
)

if question:
    st.session_state.chat_messages.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.markdown(question)

    try:
        result = answer_question(selected_id, question)

        response = result["answer"]

        with st.chat_message("assistant"):
            st.markdown(response)
            st.caption(
                f"Detected intent: {result['intent']} | "
                f"Model confidence: {result['confidence']:.2f}"
            )

        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": response
        })

    except Exception as e:
        st.error(f"Error: {type(e).__name__}: {e}")
        st.exception(e)

