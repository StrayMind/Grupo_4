"""
scripts/train_fraud_model.py
Entrenamiento del modelo de detección de fraude usando datos de Supabase.
"""

import os
import json
from pathlib import Path

import joblib
import pandas as pd
import psycopg
from dotenv import load_dotenv
from sklearn.compose import ColumnTransformer
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

load_dotenv()

ARTIFACTS_DIR = Path("artifacts")
ARTIFACTS_DIR.mkdir(exist_ok=True)

# CORRECCIÓN: El target real en la base de datos es is_fraud
TARGET_COL = "is_fraud"

def get_connection_params():
    return {
        "host": os.getenv("SUPABASE_DB_HOST"),
        "port": os.getenv("SUPABASE_DB_PORT", "5432"),
        "dbname": os.getenv("SUPABASE_DB_NAME", "postgres"),
        "user": os.getenv("SUPABASE_DB_USER"),
        "password": os.getenv("SUPABASE_DB_PASSWORD"),
        "sslmode": "require",
    }

def load_dataset():
    # Seleccionamos las columnas validadas que subimos en el paso de carga
    query = '''
    SELECT
        cc_num, 
        merchant, 
        category, 
        amt, 
        gender,
        street,
        city, 	
        state, 	
        zip,	
        lat, 	
        long, 	
        job, 	
        dob, 	
        unix_time, 	
        merch_lat, 	
        merch_long, 	
        is_fraud
    FROM public.fraudtest_demo
    WHERE is_fraud IS NOT NULL;
    '''

    print("Conectando a la base de datos para extraer datos...")
    with psycopg.connect(**get_connection_params()) as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            # Obtenemos los nombres de las columnas y los datos directamente
            columns = [desc[0] for desc in cur.description]
            data = cur.fetchall()
            df = pd.DataFrame(data, columns=columns)


    df[TARGET_COL] = df[TARGET_COL].astype(int)
    
    return df

def build_pipeline(X: pd.DataFrame):
    categorical_features = X.select_dtypes(include=["object", "string"]).columns.tolist()
    numeric_features = [c for c in X.columns if c not in categorical_features]

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1), categorical_features),
            ("num", "passthrough", numeric_features),
        ]
    )

    model = DecisionTreeClassifier(
        max_depth=12, 
        class_weight="balanced",
        random_state=42
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    return pipeline, categorical_features, numeric_features

def main():
    print("Iniciando extracción de datos desde Supabase...")
    df = load_dataset()
    print(f"Dataset cargado correctamente. Dimensiones: {df.shape}")

    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL]

    pipeline, categorical_features, numeric_features = build_pipeline(X)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print("Entrenando el modelo Pipeline...")
    pipeline.fit(X_train, y_train)
    
    print("Evaluando el modelo...")
    y_pred = pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    conf_matrix = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(y_test, y_pred, output_dict=True)

    metrics = {
        "accuracy": float(accuracy),
        "confusion_matrix": conf_matrix,
        "classification_report": report,
        "train_rows": int(len(X_train)),
        "test_rows": int(len(X_test)),
        "categorical_features": categorical_features,
        "numeric_features": numeric_features,
    }

    print("Guardando artefactos en disco...")
    joblib.dump(pipeline, ARTIFACTS_DIR / "fraude_model.joblib")

    with open(ARTIFACTS_DIR / "fraude_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    print("\n=== Entrenamiento completado exitosamente ===")
    print(f"Accuracy: {accuracy:.4f}")
    print(f"Modelo guardado en: {ARTIFACTS_DIR / 'fraude_model.joblib'}")
    print(f"Métricas guardadas en: {ARTIFACTS_DIR / 'fraude_metrics.json'}")

if __name__ == "__main__":
    main()
