import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

def get_connection_params():
    return {
        "host": os.getenv("SUPABASE_DB_HOST"),
        "port": os.getenv("SUPABASE_DB_PORT", "5432"),
        "dbname": os.getenv("SUPABASE_DB_NAME", "postgres"),
        "user": os.getenv("SUPABASE_DB_USER"),
        "password": os.getenv("SUPABASE_DB_PASSWORD"),
        "sslmode": "require",
    }

def test_connection():
    params = get_connection_params()
    missing = [k for k, v in params.items() if k != "sslmode" and not v]
    if missing:
        return {"status": "error", "detail": "Faltan variables: " + ", ".join(missing)}
    try:
        with psycopg.connect(**params) as conn:
            with conn.cursor() as cur:
                cur.execute("select version();")
                version = cur.fetchone()[0]
        return {"status": "ok", "detail": "Conexión exitosa", "db_version": version}
    except Exception as e:
        return {"status": "error", "detail": str(e)}

def get_fraudtest(limit=20):
    params = get_connection_params()
    missing = [k for k, v in params.items() if k != "sslmode" and not v]
    if missing:
        raise ValueError("Faltan variables: " + ", ".join(missing))

    query = """
    select
        trans_date_trans_time, cc_num, merchant, category, amt,
        gender, street, city, state, zip, lat, long, job, dob,
        unix_time, merch_lat, merch_long, is_fraud
    from public.fraudtest_demo
    order by ctid
    limit %s;
    """

    with psycopg.connect(**params) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (limit,))
            rows = cur.fetchall()
            columns = [desc.name for desc in cur.description]

    results = []
    for row in rows:
        item = {}
        for col, value in zip(columns, row):
            item[col] = value.isoformat() if hasattr(value, "isoformat") else value
        results.append(item)
    return results

def get_fraudtest_stats():
    params = get_connection_params()
    missing = [k for k, v in params.items() if k != "sslmode" and not v]
    if missing:
        raise ValueError("Faltan variables: " + ", ".join(missing))

    summary_query = """
    select
        count(*)                          as total_transacciones,
        sum(is_fraud)                     as total_fraudes,
        round(avg(amt)::numeric, 2)       as promedio_monto,
        round(max(amt)::numeric, 2)       as monto_maximo,
        round(min(amt)::numeric, 2)       as monto_minimo
    from public.fraudtest_demo;
    """

    category_query = """
    select category, count(*) as total, sum(is_fraud) as fraudes
    from public.fraudtest_demo
    group by category
    order by fraudes desc
    limit 10;
    """

    gender_query = """
    select gender, count(*) as total, sum(is_fraud) as fraudes
    from public.fraudtest_demo
    group by gender
    order by gender;
    """

    with psycopg.connect(**params) as conn:
        with conn.cursor() as cur:
            cur.execute(summary_query)
            summary = cur.fetchone()
            cur.execute(category_query)
            by_category = cur.fetchall()
            cur.execute(gender_query)
            by_gender = cur.fetchall()

    return {
        "total_transacciones": int(summary[0]) if summary[0] else 0,
        "total_fraudes": int(summary[1]) if summary[1] else 0,
        "promedio_monto": float(summary[2]) if summary[2] else None,
        "monto_maximo": float(summary[3]) if summary[3] else None,
        "monto_minimo": float(summary[4]) if summary[4] else None,
        "fraudes_por_categoria": [
            {"category": r[0], "total": int(r[1]), "fraudes": int(r[2])}
            for r in by_category
        ],
        "fraudes_por_genero": [
            {"gender": r[0], "total": int(r[1]), "fraudes": int(r[2])}
            for r in by_gender
        ],
    }