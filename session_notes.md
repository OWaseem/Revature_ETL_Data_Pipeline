# ETL Project — Session Notes

## Session: 2026-06-04

### What We Covered

#### Reader Layer Philosophy
- Each reader returns a **pandas DataFrame** so the rest of the pipeline doesn't care about the source format
- Readers should be functions that accept a `path` argument — never hardcode paths or run logic at module level (importing would trigger execution)

#### csv_reader.py — COMPLETE
```python
import pandas as pd

def read_csv(path):
    return pd.read_csv(path)
```

#### json_reader.py — COMPLETE
```python
import pandas as pd
import json

def read_json(path, record_path=None):
    with open(path, 'r') as f:
        data_dict = json.load(f)

    if record_path is not None:
        return pd.json_normalize(data_dict, record_path)
    else:
        return pd.DataFrame(data_dict)
```
- Handles both flat list JSON and nested dict JSON via optional `record_path` argument

#### config.py — COMPLETE
```python
import yaml

def load_sources(path):
    with open(path, 'r') as f:
        yaml_data = yaml.safe_load(f)
    return yaml_data.get('sources', [])
```

#### sources.yml — COMPLETE
```yaml
sources:
  # JSON
  - name: airports
    record_path: airports
    format: json
    path: data/airports.json

  # CSV
  - name: ai_student
    format: csv
    path: data/ai_student_impact_dataset.csv
  
  # API
  - name: dad_jokes
    record_path: results
    format: api
    url: https://icanhazdadjoke.com/search
```

#### api_reader.py — ALMOST COMPLETE (needs one fix)
```python
import requests
import pandas as pd

def read_api(url, record_path=None):   # <-- was mistakenly named readapi, fix to read_api
    response = requests.get(url, headers={"Accept": "application/json"})
    data_dict = response.json()

    if record_path is not None:
        return pd.json_normalize(data_dict, record_path)
    else:
        return pd.DataFrame(data_dict)
```

---

### Next Steps

1. **Fix** `readapi` → `read_api` in `api_reader.py`
2. **main.py** — loads `sources.yml`, calls the right reader per source format, orchestrates the pipeline
3. **validate.py** — schema conformity, null checks, domain rules
4. **clean.py** — fix/drop invalid data, normalize column names
5. **load.py** — batch UPSERT into PostgreSQL staging tables using raw psycopg2 SQL
6. **rules.py** — validation rule definitions
7. **tests/** — 80%+ pytest coverage required
