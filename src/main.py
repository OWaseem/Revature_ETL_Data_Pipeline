from config import load_sources
from readers.csv_reader import read_csv
from readers.json_reader import read_json
from readers.api_reader import read_api

sources = load_sources("config/sources.yml")

for source in sources:
    if source["format"] == "csv":
       print(read_csv(source["path"]))
    elif source["format"] == "json":
        print(read_json(source["path"], source.get("record_path", None)))
    elif source["format"] == "api":
        print(read_api(source["url"], source.get("record_path", None)))