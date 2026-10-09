
from pathlib import Path

import joblib
import pandas as pd

from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "intents.csv"
MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "intent_classifier.joblib"


def train_model():
    """Train and save the intent classification pipeline."""

    data = pd.read_csv(DATA_PATH)

    if data.empty or data["intent"].nunique() < 2:
        raise ValueError("Training data needs multiple intent classes.")

    if data[["text", "intent"]].isnull().any().any():
        raise ValueError("Training data contains missing values.")

    model = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                ngram_range=(1, 2),
                strip_accents="unicode"
            )
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                class_weight=None,
                random_state=42
            )
        )
    ])

    model.fit(data["text"], data["intent"])

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"Model saved to: {MODEL_PATH}")
    print(f"Training examples: {len(data)}")
    print(f"Intent classes: {data['intent'].nunique()}")


def load_model():
    """Load the previously trained model."""

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            "Model not found. Run: python -m src.nlp_engine"
        )

    return joblib.load(MODEL_PATH)



def predict_intent(model, text):
    """Predict an intent with a conservative unknown-query fallback."""

    if not text or not text.strip():
        return "unknown", 0.0

    probabilities = model.predict_proba([text])[0]
    classifier = model.named_steps["classifier"]

    best_index = probabilities.argmax()
    intent = classifier.classes_[best_index]
    confidence = float(probabilities[best_index])

    # Reject only very low-confidence predictions for now.
    # This threshold must be calibrated using held-out test data.
    if confidence < 0.4:
        return "unknown", confidence

    return intent, confidence



if __name__ == "__main__":
    train_model()
