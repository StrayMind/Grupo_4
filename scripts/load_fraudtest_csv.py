"""
scripts/load_fraudtest_csv.py
Carga el CSV preprocesado de fraude a Supabase
"""

import logging
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv
from psycopg import sql

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

CSV_PATH = Path("data/processed/fraudtest_validado.csv")
TABLE_NAME = "public.fraudtest_demo"
DROP_AND_RECREATE_TABLE = True
CLEAR_BEFORE_INSERT = False

def get_connection_params():
    return {
        "host": os.getenv("SUPABASE_DB_HOST"),
        "port": os.getenv("SUPABASE_DB_PORT", "5432"),
        "dbname": os.getenv("SUPABASE_DB_NAME", "postgres"),
        "user": os.getenv("SUPABASE_DB_USER"),
        "password": os.getenv("SUPABASE_DB_PASSWORD"),
        "sslmode": "require",
    }

def validate_env():
    params = get_connection_params()
    missing = [k for k, v in params.items() if k != "sslmode" and not v]
    if missing:
        raise ValueError("Faltan variables de entorno: " + ", ".join(missing))
    return params

def load_dataframe():
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {CSV_PATH}")
    return pd.read_csv(CSV_PATH)

def infer_postgres_type(series):
    dtype = str(series.dtype)
    if "int" in dtype:
        return "BIGINT"
    if "float" in dtype:
        return "DOUBLE PRECISION"
    if "bool" in dtype:
        return "BOOLEAN"
    if "datetime" in dtype:
        return "TIMESTAMP"
    return "TEXT"

def table_identifier(table_name):
    return sql.Identifier(*table_name.split("."))

def column_identifiers(columns):
    return sql.SQL(", ").join(sql.Identifier(str(col)) for col in columns)

def clear_table(conn):
    query = sql.SQL("truncate table {} restart identity;").format(table_identifier(TABLE_NAME))
    with conn.cursor() as cur:
        cur.execute(query)

def drop_table(conn):
    query = sql.SQL("drop table if exists {};").format(table_identifier(TABLE_NAME))
    with conn.cursor() as cur:
        cur.execute(query)

def create_table_from_dataframe(conn, df):
    if df.empty:
        raise ValueError("No se puede crear la tabla: el DataFrame está vacío.")
    col_defs = [
        sql.SQL("{} {}").format(
            sql.Identifier(str(col)),
            sql.SQL(infer_postgres_type(df[col]))
        )
        for col in df.columns
    ]
    query = sql.SQL("create table {} ({});").format(
        table_identifier(TABLE_NAME),
        sql.SQL(", ").join(col_defs),
    )
    with conn.cursor() as cur:
        cur.execute(query)

def insert_dataframe(conn, df):
    columns = list(df.columns)
    placeholders = sql.SQL(", ").join(sql.Placeholder() for _ in columns)
    query = sql.SQL("insert into {} ({}) values ({})").format(
        table_identifier(TABLE_NAME),
        column_identifiers(columns),
        placeholders,
    )

    BATCH_SIZE = 5000
    total = 0
    rows = list(df.itertuples(index=False, name=None))

    for i in range(0, len(rows), BATCH_SIZE):
        batch = rows[i:i + BATCH_SIZE]
        with conn.cursor() as cur:
            cur.executemany(query, batch)
        conn.commit()
        total += len(batch)
        logger.info(f"Insertadas {total} / {len(rows)} filas...")

    return total

def add_event(report, process_start, step, status="OK", detail="", step_start=None):
    now = datetime.now()
    elapsed = round((now - process_start).total_seconds(), 2)
    duration = round((now - step_start).total_seconds(), 2) if step_start else None
    report.append({
        "momento": now.strftime("%Y-%m-%d %H:%M:%S"),
        "segundos_desde_inicio": elapsed,
        "duracion_paso_segundos": duration,
        "paso": step,
        "estado": status,
        "detalle": detail,
    })
    logger.info(f"[{status}] {step}: {detail}")

def run_load_process():
    report = []
    process_start = datetime.now()
    inserted_rows = 0

    try:
        add_event(report, process_start, step="Inicio del proceso",
                  detail="Carga directa del CSV de fraude hacia Supabase/PostgreSQL.")

        step_start = datetime.now()
        params = validate_env()
        add_event(report, process_start, step="Validación de variables de entorno",
                  detail="Credenciales disponibles en archivo .env.", step_start=step_start)

        step_start = datetime.now()
        df = load_dataframe()
        add_event(report, process_start, step="Lectura del CSV",
                  detail=f"Leído correctamente: {len(df)} filas y {len(df.columns)} columnas.",
                  step_start=step_start)

        step_start = datetime.now()
        with psycopg.connect(**params) as conn:
            add_event(report, process_start, step="Conexión a Supabase/PostgreSQL",
                      detail="Conexión establecida correctamente.", step_start=step_start)

            if DROP_AND_RECREATE_TABLE:
                step_start = datetime.now()
                drop_table(conn)
                create_table_from_dataframe(conn, df)
                add_event(report, process_start, step="Recreación de tabla destino",
                          detail=f"Tabla {TABLE_NAME} eliminada y recreada según estructura del CSV.",
                          step_start=step_start)
            elif CLEAR_BEFORE_INSERT:
                step_start = datetime.now()
                clear_table(conn)
                add_event(report, process_start, step="Limpieza de tabla destino",
                          detail=f"Tabla {TABLE_NAME} limpiada con TRUNCATE.", step_start=step_start)
            else:
                add_event(report, process_start, step="Modo incremental",
                          detail="Los registros se agregarán al final de la tabla existente.")

            step_start = datetime.now()
            inserted_rows = insert_dataframe(conn, df)
            add_event(report, process_start, step="Inserción de registros",
                      detail=f"Se insertaron {inserted_rows} filas en {TABLE_NAME}.",
                      step_start=step_start)

            step_start = datetime.now()
            conn.commit()
            add_event(report, process_start, step="Confirmación de transacción",
                      detail="Commit ejecutado correctamente.", step_start=step_start)

        add_event(report, process_start, step="Fin del proceso",
                  detail="Carga completada exitosamente.")

    except Exception as error:
        add_event(report, process_start, step="Error del proceso",
                  status="ERROR", detail=str(error))
        raise

    return inserted_rows, report

if __name__ == "__main__":
    inserted, report = run_load_process()
    print(f"\nTotal de filas insertadas: {inserted}")
    print(f"Tabla destino: {TABLE_NAME}")