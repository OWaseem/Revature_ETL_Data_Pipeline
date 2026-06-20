import json
from config import load_sources
from readers.csv_reader import read_csv
from readers.json_reader import read_json
from readers.api_reader import read_api


def get_airport_coords(city):
    with open("data/airports.json", "r") as f:
        airports = json.load(f)["airports"]
    for airport in airports:
        if airport["city"].lower() == city.lower():
            return airport["lat"], airport["lon"]
    return None, None


if __name__ == "__main__":
    sources = load_sources("config/sources.yml")

    for source in sources:
        if source["format"] == "csv":
            print(read_csv(source["path"]))

        elif source["format"] == "json":
            print(read_json(source["path"], source.get("record_path")))

        elif source["format"] == "api" and source["name"] == "weather":
            flights_df = read_csv("data/flights.csv")
            cities = flights_df["arrival_city"].unique()
            for city in cities:
                lat, lon = get_airport_coords(city)
                if lat is None:
                    print(f"No coordinates found for {city}, skipping.")
                    continue
                url = f"{source['url']}&latitude={lat}&longitude={lon}"
                df = read_api(url, source.get("record_path"))
                df["city"] = city
                print(df)
