import os
import pytest
import psycopg2
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture
def test_db(monkeypatch):
    # point all database calls to test_ingest_db and clean up after
    monkeypatch.setenv("DB_NAME", os.getenv("TEST_DB_NAME"))
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


def test_main_runs_without_error(test_db):
    # full pipeline should run against test_ingest_db without raising
    from main import main
    main()


def test_main_loads_cities(test_db):
    # after running, stg_cities should have rows from airports.json
    from main import main
    main()
    cursor = test_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM stg_cities;")
    count = cursor.fetchone()[0]
    cursor.close()
    assert count > 0


def test_main_loads_flights(test_db):
    # after running, stg_flights should have valid rows
    from main import main
    main()
    cursor = test_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM stg_flights;")
    count = cursor.fetchone()[0]
    cursor.close()
    assert count > 0


def test_main_populates_rejects(test_db):
    # after running, stg_rejects should have rows from dirty data
    from main import main
    main()
    cursor = test_db.cursor()
    cursor.execute("SELECT COUNT(*) FROM stg_rejects;")
    count = cursor.fetchone()[0]
    cursor.close()
    assert count > 0
