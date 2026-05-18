"""
scripts/limpieza_fraud_pipeline.py
Pipeline de preprocesamiento - Detección de Fraude
"""

import logging
from pathlib import Path

import pandas as pd
from sklearn.preprocessing import LabelEncoder

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

INPUT_FILE = Path("data/02_fraudTest.csv")
OUTPUT_FILE = Path("data/02_fraudTest_preprocesado_v2.csv")
TARGET_COL = "is_fraud"
METODO_CODIFICACION = "label"

COLS_A_ELIMINAR = [
    "Unnamed: 0",
    "first",
    "last",
    "city_pop",
    "trans_num",
]

COLS_CATEGORICAS = [
    "merchant",
    "category",
    "gender",
    "street",
    "city",
    "state",
    "zip",
    "job",
    "dob",
]

def cargar_datos(input_file):
    logger.info(f"Cargando datos desde: {input_file}")
    df = pd.read_csv(input_file)
    logger.info(f"Shape inicial: {df.shape}")
    return df

def eliminar_columnas(df, cols):
    cols_presentes = [c for c in cols if c in df.columns]
    df = df.drop(columns=cols_presentes)
    logger.info(f"Columnas eliminadas: {cols_presentes}")
    return df

def codificar_categoricas(df, cols_categoricas, metodo="label"):
    cols_presentes = [c for c in cols_categoricas if c in df.columns]
    if metodo == "label":
        le = LabelEncoder()
        for col in cols_presentes:
            df[col] = le.fit_transform(df[col].astype(str))
        logger.info(f"Label encoding aplicado a: {cols_presentes}")
    elif metodo == "onehot":
        df = pd.get_dummies(df, columns=cols_presentes)
        logger.info(f"One-hot encoding aplicado a: {cols_presentes}")
    else:
        raise ValueError(f"Método no válido: '{metodo}'. Usa 'label' u 'onehot'.")
    return df

def guardar_datos(df, output_file):
    df.to_csv(output_file, index=False)
    logger.info(f"Dataset preprocesado guardado en: {output_file} | Shape: {df.shape}")

def run_pipeline():
    df = cargar_datos(INPUT_FILE)
    df = eliminar_columnas(df, COLS_A_ELIMINAR)
    df = codificar_categoricas(df, COLS_CATEGORICAS, metodo=METODO_CODIFICACION)
    guardar_datos(df, OUTPUT_FILE)
    logger.info("Pipeline finalizado correctamente.")
    return df

if __name__ == "__main__":
    df_preprocesado = run_pipeline()
    print(f"\nShape final: {df_preprocesado.shape}")
    print(f"Distribución de '{TARGET_COL}':\n{df_preprocesado[TARGET_COL].value_counts()}")