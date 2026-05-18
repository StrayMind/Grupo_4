"""
scripts/validate_fraudtest.py
Validación estructural y semántica del dataset de fraude preprocesado.
"""

import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

INPUT_PATH = Path("data/02_fraudTest_preprocesado_v2.csv")
OUTPUT_DIR = Path("data/processed")
OUTPUT_PATH = OUTPUT_DIR / "fraudtest_validado.csv"
LOG_PATH = OUTPUT_DIR / "validation_log.csv"

EXPECTED_COLUMNS = [
    "trans_date_trans_time", "cc_num", "merchant", "category", "amt",
    "gender", "street", "city", "state", "zip", "lat", "long",
    "job", "dob", "unix_time", "merch_lat", "merch_long", "is_fraud",
]

SEMANTIC_RULES = {
    "amt":        (0.0, 100_000.0),
    "lat":        (-90.0, 90.0),
    "long":       (-180.0, 180.0),
    "merch_lat":  (-90.0, 90.0),
    "merch_long": (-180.0, 180.0),
    "gender":     (0, 1),
    "is_fraud":   (0, 1),
}

validation_log = []

def log_check(step, status, detail):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    validation_log.append({"momento": now, "paso": step, "estado": status, "detalle": detail})
    logger.info(f"[{status}] {step}: {detail}")

def leer_dataset():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {INPUT_PATH}")
    df = pd.read_csv(INPUT_PATH)
    log_check("Lectura del dataset", "OK",
              f"Leído correctamente: {len(df)} filas y {len(df.columns)} columnas.")
    return df

def validar_columnas(df):
    presentes = set(df.columns)
    esperadas = set(EXPECTED_COLUMNS)
    faltantes = esperadas - presentes
    extra = presentes - esperadas
    if faltantes:
        log_check("Validación de columnas", "WARN", f"Columnas faltantes: {sorted(faltantes)}")
    if extra:
        log_check("Validación de columnas", "INFO", f"Columnas extra: {sorted(extra)}")
    if not faltantes and not extra:
        log_check("Validación de columnas", "OK", "Todas las columnas esperadas están presentes.")
    return df

def convertir_tipos(df):
    if "trans_date_trans_time" in df.columns:
        df["trans_date_trans_time"] = pd.to_datetime(df["trans_date_trans_time"], errors="coerce")
    log_check("Conversión de tipos", "OK", "trans_date_trans_time convertida a datetime64.")
    return df

def eliminar_duplicados(df):
    n_antes = len(df)
    df = df.drop_duplicates()
    eliminados = n_antes - len(df)
    estado = "OK" if eliminados == 0 else "WARN"
    log_check("Eliminación de duplicados", estado, f"Filas duplicadas eliminadas: {eliminados}.")
    return df

def eliminar_nulos(df):
    n_antes = len(df)
    nulos_por_col = df.isna().sum()
    cols_con_nulos = nulos_por_col[nulos_por_col > 0]
    if not cols_con_nulos.empty:
        log_check("Detección de nulos", "WARN", f"Columnas con nulos: {cols_con_nulos.to_dict()}")
        df = df.dropna()
        log_check("Eliminación de nulos", "OK", f"Filas eliminadas por nulos: {n_antes - len(df)}.")
    else:
        log_check("Detección de nulos", "OK", "No se encontraron valores nulos.")
    return df

def validar_rangos_semanticos(df):
    n_antes = len(df)
    mask_valido = pd.Series([True] * len(df), index=df.index)
    for col, (min_val, max_val) in SEMANTIC_RULES.items():
        if col not in df.columns:
            continue
        fuera = ~df[col].between(min_val, max_val)
        n_fuera = fuera.sum()
        if n_fuera > 0:
            log_check(f"Rango semántico: {col}", "WARN",
                      f"{n_fuera} filas fuera del rango [{min_val}, {max_val}].")
            mask_valido &= ~fuera
        else:
            log_check(f"Rango semántico: {col}", "OK",
                      f"Todos los valores dentro del rango [{min_val}, {max_val}].")
    df = df[mask_valido].reset_index(drop=True)
    eliminados = n_antes - len(df)
    if eliminados > 0:
        log_check("Filtro de rangos semánticos", "OK",
                  f"Filas eliminadas por rangos inválidos: {eliminados}.")
    return df

def resumen_final(df):
    log_check("Resumen final", "OK",
              f"Filas: {len(df)} | Columnas: {len(df.columns)} | "
              f"Duplicados: {df.duplicated().sum()} | Nulos: {df.isna().sum().sum()}")

def guardar_resultados(df):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    log_check("Guardado del dataset procesado", "OK", f"Dataset guardado en: {OUTPUT_PATH}")
    log_df = pd.DataFrame(validation_log)
    log_df.to_csv(LOG_PATH, index=False)
    log_check("Guardado del log de validación", "OK", f"Log guardado en: {LOG_PATH}")

def run_validation_pipeline():
    logger.info("=== Inicio del pipeline de validación ===")
    df = leer_dataset()
    df = validar_columnas(df)
    df = convertir_tipos(df)
    df = eliminar_duplicados(df)
    df = eliminar_nulos(df)
    df = validar_rangos_semanticos(df)
    resumen_final(df)
    guardar_resultados(df)
    logger.info("=== Pipeline de validación finalizado ===")
    return df

if __name__ == "__main__":
    df_validado = run_validation_pipeline()
    print(f"\nDataset validado: {len(df_validado)} filas | {len(df_validado.columns)} columnas")
    print(f"Guardado en: {OUTPUT_PATH}")
    print(f"Log guardado en: {LOG_PATH}")