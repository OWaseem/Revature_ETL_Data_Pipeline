import os
import json
import math
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def _serialize(obj):
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    if isinstance(obj, float) and math.isnan(obj):
        return None
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def load_rejects(rejects_df):
    if rejects_df.empty:
        return

    conn = get_connection()
    cursor = conn.cursor()

    try:
        sql = """
            INSERT INTO stg_rejects (source_name, raw_payload, reason)
            VALUES (%s, %s, %s);
        """

        for _, row in rejects_df.iterrows():
            payload = row["raw_payload"]
            if isinstance(payload, dict):
                payload = {k: (None if isinstance(v, float) and math.isnan(v) else v)
                          for k, v in payload.items()}
            cursor.execute(sql, (
                row["source_name"],
                json.dumps(payload, default=_serialize),
                row["reason"]
            ))

        conn.commit()

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()


def load(df, target_table, pk, source_name=None):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        columns = list(df.columns)
        placeholders = ", ".join(["%s"] * len(columns))
        col_names = ", ".join(columns)
        updates = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns if col != pk])

        sql = f"""
            INSERT INTO {target_table} ({col_names})
            VALUES ({placeholders})
            ON CONFLICT ({pk}) DO UPDATE
            SET {updates};
        """

        for _, row in df.iterrows():
            try:
                values = tuple(row[col] for col in columns)
                cursor.execute(sql, values)
                conn.commit()
            except psycopg2.errors.ForeignKeyViolation:
                conn.rollback()
                reject = pd.DataFrame([{
                    "source_name": source_name or target_table,
                    "raw_payload": row.to_dict(),
                    "reason": f"FK violation: {row[pk]} references a city not in stg_cities"
                }])
                load_rejects(reject)

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        conn.close()
