import os
import pytest
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def test_conn():
    # connects to test_ingest_db and cleans up tables after each test
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("TEST_DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )
    yield conn
    cursor = conn.cursor()
    cursor.execute("TRUNCATE stg_flights, stg_hotels, stg_weather, stg_rejects, stg_cities CASCADE;")
    conn.commit()
    cursor.close()
    conn.close()


def test_load_inserts_row(test_conn, monkeypatch):
    # a valid row should be inserted into stg_cities
    from load import load
    monkeypatch.setenv("DB_NAME", os.getenv("TEST_DB_NAME"))

    df = pd.DataFrame([{
        "city": "Dubai", "code": "DXB", "country": "AE",
        "lat": 25.2528, "lon": 55.3644, "name": "Dubai International"
    }])
    load(df, "stg_cities", "city", "airports")

    cursor = test_conn.cursor()
    cursor.execute("SELECT city FROM stg_cities WHERE city = 'Dubai';")
    row = cursor.fetchone()
    cursor.close()
    assert row is not None
    assert row[0] == "Dubai"


def test_load_upsert_does_not_duplicate(test_conn, monkeypatch):
    # loading the same row twice should result in only one row (UPSERT)
    from load import load
    monkeypatch.setenv("DB_NAME", os.getenv("TEST_DB_NAME"))

    df = pd.DataFrame([{
        "city": "Tokyo", "code": "NRT", "country": "JP",
        "lat": 35.772, "lon": 140.3929, "name": "Narita International"
    }])
    load(df, "stg_cities", "city", "airports")
    load(df, "stg_cities", "city", "airports")

    cursor = test_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM stg_cities WHERE city = 'Tokyo';")
    count = cursor.fetchone()[0]
    cursor.close()
    assert count == 1


def test_load_rejects_writes_to_table(test_conn, monkeypatch):
    # rejected rows should be written to stg_rejects with correct source and reason
    from load import load_rejects
    monkeypatch.setenv("DB_NAME", os.getenv("TEST_DB_NAME"))

    rejects_df = pd.DataFrame([{
        "source_name": "flights",
        "raw_payload": {"flight_id": "FL005", "delay_minutes": -10},
        "reason": "delay_minutes failed: value >= 0"
    }])
    load_rejects(rejects_df)

    cursor = test_conn.cursor()
    cursor.execute("SELECT source_name, reason FROM stg_rejects;")
    row = cursor.fetchone()
    cursor.close()
    assert row[0] == "flights"
    assert "delay_minutes" in row[1]


def test_get_city_coords_returns_coords(test_conn, monkeypatch):
    # get_city_coords should return lat/lon for a known city
    from load import load, get_city_coords
    monkeypatch.setenv("DB_NAME", os.getenv("TEST_DB_NAME"))

    df = pd.DataFrame([{
        "city": "London", "code": "LHR", "country": "GB",
        "lat": 51.47, "lon": -0.4543, "name": "London Heathrow"
    }])
    load(df, "stg_cities", "city", "airports")

    canonical_city, lat, lon = get_city_coords("London")
    assert canonical_city == "London"
    assert lat is not None
    assert lon is not None


def test_get_city_coords_returns_none_for_unknown(monkeypatch):
    # get_city_coords should return None, None, None for a city not in stg_cities
    from load import get_city_coords
    monkeypatch.setenv("DB_NAME", os.getenv("TEST_DB_NAME"))

    canonical_city, lat, lon = get_city_coords("Atlantis")
    assert canonical_city is None
    assert lat is None
    assert lon is None


def test_fk_violation_logged_to_rejects(test_conn, monkeypatch):
    # loading a flight with an arrival_city not in stg_cities should log to stg_rejects
    from load import load
    monkeypatch.setenv("DB_NAME", os.getenv("TEST_DB_NAME"))

    df = pd.DataFrame([{
        "flight_id": "FL999",
        "departure_city": "New York",
        "arrival_city": "UnknownCity",
        "departure_time": None,
        "arrival_time": None,
        "delay_minutes": 0,
        "airline": "Test Air"
    }])
    load(df, "stg_flights", "flight_id", "flights")

    cursor = test_conn.cursor()
    cursor.execute("SELECT reason FROM stg_rejects WHERE source_name = 'flights' AND reason LIKE '%FK violation%';")
    row = cursor.fetchone()
    cursor.close()
    assert row is not None
    assert "FK violation" in row[0]


def test_load_rejects_empty_df_does_nothing(monkeypatch):
    # load_rejects with an empty DataFrame should return without hitting the database
    from load import load_rejects
    monkeypatch.setenv("DB_NAME", os.getenv("TEST_DB_NAME"))

    rejects_df = pd.DataFrame()
    load_rejects(rejects_df)  # should not raise


def test_serialize_timestamp(monkeypatch):
    # _serialize should convert timestamps to isoformat strings
    from load import _serialize
    import pandas as pd
    ts = pd.Timestamp("2026-06-15 08:00")
    result = _serialize(ts)
    assert result == "2026-06-15T08:00:00"


def test_serialize_nan(monkeypatch):
    # _serialize should convert NaN floats to None
    from load import _serialize
    import math
    result = _serialize(float("nan"))
    assert result is None


def test_serialize_unsupported_type():
    # _serialize should raise TypeError for unsupported types
    from load import _serialize
    with pytest.raises(TypeError):
        _serialize(object())
