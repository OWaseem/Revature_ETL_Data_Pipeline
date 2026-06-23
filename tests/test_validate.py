import pandas as pd
from validate import validate

def test_row_rejected_when_delay_negative():
    # A row with delay_minutes < 0 should be rejected
    df = pd.DataFrame([{"delay_minutes": -5}])
    rules = [{"column": "delay_minutes", "condition": "value >= 0"}]
    valid_df, rejects_df = validate(df, "flights", rules)
    assert len(valid_df) == 0
    assert len(rejects_df) == 1

def test_valid_row_passes():
    # A row that satisfies all rules should be in valid_df, not rejects
    df = pd.DataFrame([{"delay_minutes": 10}])
    rules = [{"column": "delay_minutes", "condition": "value >= 0"}]
    valid_df, rejects_df = validate(df, "flights", rules)
    assert len(valid_df) == 1
    assert len(rejects_df) == 0

def test_null_value_rejected():
    # A null arrival_city should fail the not-null rule
    df = pd.DataFrame([{"arrival_city": None}])
    rules = [{"column": "arrival_city", "condition": "value is not None and not pd.isna(value)"}]
    valid_df, rejects_df = validate(df, "flights", rules)
    assert len(valid_df) == 0
    assert len(rejects_df) == 1

def test_mixed_rows_split_correctly():
    # 2 valid rows and 1 invalid — make sure counts are right
    df = pd.DataFrame([
        {"delay_minutes": 10},
        {"delay_minutes": 0},
        {"delay_minutes": -1},
    ])
    rules = [{"column": "delay_minutes", "condition": "value >= 0"}]
    valid_df, rejects_df = validate(df, "flights", rules)
    assert len(valid_df) == 2
    assert len(rejects_df) == 1

def test_empty_rules_passes_all():
    # With no rules, every row should pass validation
    df = pd.DataFrame([{"city": "Dubai"}, {"city": "Tokyo"}])
    rules = []
    valid_df, rejects_df = validate(df, "weather", rules)
    assert len(valid_df) == 2
    assert len(rejects_df) == 0

def test_reject_reason_recorded():
    # The reject record should contain the column and condition that failed
    df = pd.DataFrame([{"delay_minutes": -5}])
    rules = [{"column": "delay_minutes", "condition": "value >= 0"}]
    valid_df, rejects_df = validate(df, "flights", rules)
    assert "delay_minutes" in rejects_df.iloc[0]["reason"]
