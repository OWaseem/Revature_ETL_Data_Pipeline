import pandas as pd
import json


def read_json(path, record_path=None):

    with open(path, 'r') as f:
        data_dict = json.load(f)

    if record_path is not None:
        return pd.json_normalize(data_dict, record_path)
    else:
        return pd.DataFrame(data_dict)