import pandas as pd


def read_csv(path):
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {path}")
    except Exception as e:
        raise Exception(f"Failed to read CSV file {path}: {e}")
