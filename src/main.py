import json
from config import load_sources
from readers.csv_reader import read_csv
from readers.json_reader import read_json
from readers.api_reader import read_api
from clean import clean
from validate import validate
from load import load, load_rejects


def get_airport_coords(city):
    with open("data/airports.json", "r") as f:
        airports = json.load(f)["airports"]
    for airport in airports:
        if airport["city"].lower() == city.lower():
            return airport["lat"], airport["lon"]
    return None, None

def main():
    sources = load_sources("config/sources.yml")

    for source in sources:
        name = source["name"]
        rules = source.get("rules", [])
        target_table = source["target_table"]
        pk = source["pk"]

        if source["format"] == "csv":
            df = read_csv(source["path"])
            df = clean(df)
            valid_df, rejects_df = validate(df, name, rules)
            load(valid_df, target_table, pk, name)
            load_rejects(rejects_df)
            print(f"{name}: {len(valid_df)} rows loaded, {len(rejects_df)} rejected")

        elif source["format"] == "json":
            df = read_json(source["path"], source.get("record_path"))
            df = clean(df)
            valid_df, rejects_df = validate(df, name, rules)
            load(valid_df, target_table, pk, name)
            load_rejects(rejects_df)
            print(f"{name}: {len(valid_df)} rows loaded, {len(rejects_df)} rejected")
    
        elif source["format"] == "api" and name == "weather":
            flights_df = clean(read_csv("data/flights.csv"))
            cities = flights_df["arrival_city"].dropna().unique()
            for city in cities:
                try:
                    lat, lon = get_airport_coords(city)
                    if lat is None:
                        print(f"No coordinates found for {city}, skipping.")
                        continue
                    url = f"{source['url']}&latitude={lat}&longitude={lon}"
                    df = read_api(url, source.get("record_path"))
                    df["city"] = city
                    df = clean(df)
                    load(df, target_table, pk, name)
                except Exception as e:
                    print(f"Failed to process weather for {city}: {e}")
                    continue
            print(f"weather: {len(cities)} cities processed")
            

if __name__ == "__main__":
    main()