import os
import psycopg2
from flask import Flask, render_template
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

app = Flask(__name__)

LIMIT = 100

TABLE_CONFIG = {
    "cities":  {"table": "stg_cities",  "order": "city"},
    "flights": {"table": "stg_flights", "order": "flight_id"},
    "hotels":  {"table": "stg_hotels",  "order": "hotel_id"},
    "weather": {"table": "stg_weather", "order": "city"},
}


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def query(sql, params=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]
    cursor.close()
    conn.close()
    return cols, rows


def get_reject_count():
    _, rows = query("SELECT COUNT(*) FROM stg_rejects;")
    return rows[0][0]


@app.route("/")
def overview():
    _, cities = query("SELECT COUNT(*) FROM stg_cities;")
    _, flights = query("SELECT COUNT(*) FROM stg_flights;")
    _, hotels = query("SELECT COUNT(*) FROM stg_hotels;")
    _, weather = query("SELECT COUNT(*) FROM stg_weather;")
    _, rejects = query("SELECT COUNT(*) FROM stg_rejects;")
    _, rejects_by_source = query(
        "SELECT source_name, COUNT(*) FROM stg_rejects GROUP BY source_name ORDER BY COUNT(*) DESC;"
    )

    stats = {
        "cities": cities[0][0],
        "flights": flights[0][0],
        "hotels": hotels[0][0],
        "weather": weather[0][0],
        "rejects": rejects[0][0],
    }
    return render_template("overview.html", stats=stats, rejects_by_source=rejects_by_source, reject_count=get_reject_count())


@app.route("/travel")
def travel():
    cols, rows = query("SELECT * FROM vw_travel_summary ORDER BY total_flights DESC;")
    return render_template("travel.html", cols=cols, rows=rows, reject_count=get_reject_count())


@app.route("/rejects")
def rejects():
    cols, rows = query("SELECT source_name, reason, raw_payload FROM stg_rejects;")
    return render_template("rejects.html", cols=cols, rows=rows, reject_count=get_reject_count())


@app.route("/erd")
def erd():
    return render_template("erd.html", reject_count=get_reject_count())


@app.route("/table/<name>")
def table_view(name):
    if name not in TABLE_CONFIG:
        return "Not found", 404
    cfg = TABLE_CONFIG[name]
    tbl = cfg["table"]
    order = cfg["order"]

    _, total_rows = query(f"SELECT COUNT(*) FROM {tbl};")
    total = total_rows[0][0]

    cols, rows = query(f"SELECT * FROM {tbl} ORDER BY {order} LIMIT {LIMIT};")

    return render_template(
        "table_view.html",
        name=name,
        table=tbl,
        cols=cols,
        rows=rows,
        total=total,
        limit=LIMIT,
        reject_count=get_reject_count()
    )


if __name__ == "__main__":
    app.run(debug=True)
