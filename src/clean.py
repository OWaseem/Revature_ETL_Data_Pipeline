import pandas as pd


def clean(df):
    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    df = df.drop_duplicates()

    for col in ["arrival_city", "departure_city"]:
        if col in df.columns:
            df[col] = df[col].str.title()

    for col in ["delay_minutes", "price_per_night"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["departure_time", "arrival_time", "check_in", "check_out"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df
