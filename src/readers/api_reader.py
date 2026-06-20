import requests
import pandas as pd

def read_api(url, record_path=None):
    response = requests.get(url, headers={"Accept": "application/json"})
    data_dict = response.json()

    if record_path is not None:
        section = data_dict[record_path]
        if isinstance(section, list):
            return pd.json_normalize(section)
        else:
            return pd.json_normalize([section])
    else:
        return pd.DataFrame(data_dict)