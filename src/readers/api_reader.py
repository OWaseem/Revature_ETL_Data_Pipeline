import requests
import pandas as pd


def read_api(url, record_path=None):
    try:
        response = requests.get(url, headers={"Accept": "application/json"})
        response.raise_for_status()
        data_dict = response.json()

        if record_path is not None:
            section = data_dict[record_path]
            if isinstance(section, list):
                return pd.json_normalize(section)
            else:
                return pd.json_normalize([section])
        else:
            return pd.DataFrame(data_dict)

    except requests.RequestException as e:
        raise Exception(f"API request failed for {url}: {e}")
    except Exception as e:
        raise Exception(f"Failed to read API {url}: {e}")
