import pandas as pd
import math
from clean import clean

def test_whitespace_stripped():
    # Leading/trailing spaces in string columns should be removed
    df = pd.DataFrame([{"arrival_city": "  Dubai  ", "airline": "  Emirates  "}])
    result = clean(df)
    assert result["arrival_city"].iloc[0] == "Dubai"
    assert result["airline"].iloc[0] == "Emirates"

def test_city_columns_title_cased():
    # arrival_city and departure_city should be title-cased regardless of input
    df = pd.DataFrame([{"arrival_city": "new york", "departure_city": "LONDON"}])
    result = clean(df)
    assert result["arrival_city"].iloc[0] == "New York"
    assert result["departure_city"].iloc[0] == "London"

def test_duplicates_dropped():
    # Identical rows should be reduced to one
    df = pd.DataFrame([
        {"flight_id": "FL001", "airline": "Emirates"},
        {"flight_id": "FL001", "airline": "Emirates"},
    ])
    result = clean(df)
    assert len(result) == 1

def test_column_names_normalized():
    # Column names should be lowercased and spaces replaced with underscores
    df = pd.DataFrame([{"Arrival City": "Dubai", "Delay Minutes": 10}])
    result = clean(df)
    assert "arrival_city" in result.columns
    assert "delay_minutes" in result.columns

def test_numeric_coercion():
    # Non-numeric values in delay_minutes should become NaN, not crash
    df = pd.DataFrame([{"delay_minutes": "abc"}])
    result = clean(df)
    assert math.isnan(result["delay_minutes"].iloc[0])

def test_datetime_parsing():
    # String dates in departure_time should be parsed to datetime objects
    df = pd.DataFrame([{"departure_time": "2026-06-15 08:00"}])
    result = clean(df)
    assert pd.api.types.is_datetime64_any_dtype(result["departure_time"])
