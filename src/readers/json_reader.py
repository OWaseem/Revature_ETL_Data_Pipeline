import pandas as pd
import json


def read_json(path, record_path=None):
    try:
        with open(path, 'r') as f:
            data_dict = json.load(f)

        if record_path is not None:
            return pd.json_normalize(data_dict, record_path)
        else:
            return pd.DataFrame(data_dict)

    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file not found: {path}")
    except Exception as e:
        raise Exception(f"Failed to read JSON file {path}: {e}")
