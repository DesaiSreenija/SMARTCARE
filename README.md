# SmartCare AI — Intelligent Personal Health Record Assistant

SmartCare AI is an AI-powered Personal Health Record (PHR) assistant built with Python and Streamlit. It helps users manage personal health information, track medications, record health measurements, monitor appointments, and explore health trends through an interactive dashboard.

The project combines rule-based health alerts, trend analysis, and Natural Language Processing (NLP) to make personal health information easier to access and understand.

## Features

- **Patient Management:** Register and select patient profiles.
- **Medication Tracking:** View prescribed medication information and record medication doses.
- **Allergy Management:** View recorded patient allergies.
- **Health Measurement Recording:** Record heart rate, body temperature, and oxygen saturation.
- **Health Trend Analysis:** Summarize historical measurements and generate descriptive health insights.
- **Safety Alerts:** Apply configurable demonstration thresholds to flag measurements requiring attention.
- **Appointment Management:** Add and view healthcare appointments.
- **AI Health Assistant:** Ask natural-language questions about medications, medication schedules, allergies, appointments, and health trends.
- **Input Validation:** Validate patient details, measurements, and appointment information.
- **Automated Testing:** Test chatbot predictions, patient management, record creation, trend analysis, and safety alert rules.

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python |
| User interface | Streamlit |
| Data processing | Pandas |
| NLP and machine learning | Scikit-learn |
| Model serialization | Joblib |
| Database | SQLite |
| Automated testing | Pytest |

## Project Structure

```text
smartcare-ai/
├── app.py
├── requirements.txt
├── data/
│   ├── intents.csv
│   └── smartcare_intents_additional_300.csv
├── models/
│   └── intent_classifier.joblib
├── src/
│   ├── database.py
│   ├── seed_data.py
│   ├── patient_service.py
│   ├── medication_service.py
│   ├── record_service.py
│   ├── trend_service.py
│   ├── alert_service.py
│   ├── nlp_engine.py
│   └── chatbot_service.py
└── tests/
    ├── test_alert_service.py
    ├── test_chatbot.py
    ├── test_trend_service.py
    ├── test_patient_service.py
    └── test_record_service.py
```

*Note: This tree reflects the expected project layout. Adjust it if your repository uses different filenames.*

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/smartcare-ai.git
cd smartcare-ai
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Initialize the database

If the project includes database initialization and synthetic-data seeding, run the applicable project commands. For example:

```bash
python -m src.seed_data
```

Ensure the database initialization function is called as required by the application. The exact setup may vary depending on the current database implementation.

### 5. Launch the application

```bash
python -m streamlit run app.py
```

Open the local URL shown in your terminal, usually:

```text
http://localhost:8501
```

## AI and NLP Methodology

The chatbot uses a machine-learning text classification pipeline to map user questions to supported intents.

The general workflow is:

1. Collect example questions and assign intent labels.
2. Convert text into numerical features using TF-IDF.
3. Train a Logistic Regression classifier.
4. Predict the intent of a user's question.
5. Route supported intents to the appropriate health-record functionality.
6. Return a fallback response when the request is not confidently recognized.

The health insights module summarizes recorded measurements, while the safety alert module uses configurable rule-based thresholds. These are separate components: the chatbot classifies language, trend analysis summarizes measurements, and the alert engine evaluates recorded values against demonstration rules.

## Running Tests

Run the complete automated test suite:

```bash
python -m pytest -v
```

Run individual test modules:

```bash
python -m pytest tests/test_chatbot.py -v
python -m pytest tests/test_alert_service.py -v
python -m pytest tests/test_trend_service.py -v
python -m pytest tests/test_patient_service.py -v
python -m pytest tests/test_record_service.py -v
```

The current development test suite has passed **22 tests**. Test results may change as the application evolves.

## Safety, Privacy, and Limitations

- This is an academic prototype, not a clinically validated healthcare product.
- Demonstration alert thresholds are not medical diagnostic criteria.
- Health insights are informational summaries and must not be treated as medical diagnoses or treatment recommendations.
- Use synthetic data for development and demonstrations. Do not upload identifiable patient records, credentials, or sensitive health information to a public repository.
- A local SQLite database is not automatically a persistent, shared database when the app is deployed to a cloud hosting service.
- Before real-world use, the application would require appropriate security controls, access management, encryption, privacy safeguards, clinical validation, and review of applicable healthcare regulations.

## Future Enhancements

- Integration with verified electronic health record systems.
- Secure authentication and role-based access control.
- Persistent cloud database integration.
- Improved chatbot evaluation using held-out test data and per-intent precision, recall, and F1-score.
- Medication reminders and configurable notifications.
- More robust handling of missing measurements and irregular recording intervals.
- Accessibility and usability improvements.

## Academic Context

**Project:** SmartCare AI — Intelligent Personal Health Record (PHR) Assistant  
**Course:** PBMG607L — Artificial Intelligence in Healthcare  
**Application type:** Academic AI healthcare prototype

## License

No license has been specified yet. Add a license file if you intend to permit others to reuse, modify, or distribute this project.
