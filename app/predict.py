"""
scripts/predict.py
Script para realizar inferencias con el modelo de fraude entrenado.
"""

from pathlib import Path
import joblib
import pandas as pd

MODEL_PATH = Path("artifacts/fraude_model.joblib")

FEATURE_COLUMNS = [
    "merchant",
    "category",
    "amt",
    "street",
    "city",
    "state",
    "zip",
    "lat",
    "long",
    "job",
    "merch_lat",
    "merch_long"
]

def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"No existe el modelo en: {MODEL_PATH}. Asegúrate de ejecutar el entrenamiento primero.")
    return joblib.load(MODEL_PATH)

def predict_fraude(payload: dict):
    """
    Recibe un diccionario con los datos de una transacción y devuelve la predicción de fraude.
    """
    model = load_model()

    data = pd.DataFrame([payload], columns=FEATURE_COLUMNS)

    pred = model.predict(data)[0]
    probs = model.predict_proba(data)[0]

    return {
        "predicted_class": int(pred),
        "predicted_label": "FRAUDE" if int(pred) == 1 else "NORMAL",
        "probability_normal": round(float(probs[0]), 4),
        "probability_fraude": round(float(probs[1]), 4),
    }
