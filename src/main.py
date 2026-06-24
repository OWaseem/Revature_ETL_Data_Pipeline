from config import load_sources
from readers.csv_reader import read_csv
from readers.json_reader import read_json
from readers.api_reader import read_api
from clean import clean
from validate import validate
from load import load, load_rejects, get_city_coords
from log import logger

def main():
    sources = load_sources("config/sources.yml")

    for source in sources:
        name = source["name"]
        rules = source.get("rules", [])
        target_table = source["target_table"]
        pk = source["pk"]

        column_map = source.get("column_map")

        if source["format"] == "csv":
            df = read_csv(source["path"])
            logger.info(f"source={name} rows={len(df)}")
            df = clean(df, column_map)
            valid_df, rejects_df = validate(df, name, rules)
            load(valid_df, target_table, pk, name)
            load_rejects(rejects_df)
            logger.info(f"source={name} loaded={len(valid_df)} rejected={len(rejects_df)}")

        elif source["format"] == "json":
            df = read_json(source["path"], source.get("record_path"))
            logger.info(f"source={name} rows={len(df)}")
            df = clean(df, column_map)
            valid_df, rejects_df = validate(df, name, rules)
            load(valid_df, target_table, pk, name)
            load_rejects(rejects_df)
            logger.info(f"source={name} loaded={len(valid_df)} rejected={len(rejects_df)}")

        elif source["format"] == "api" and name == "weather":
            flights_df = clean(read_csv("data/flights.csv"))
            cities = flights_df["arrival_city"].dropna().unique()
            for city in cities:
                try:
                    canonical_city, lat, lon = get_city_coords(city)
                    if lat is None:
                        logger.warning(f"source={name} city={city} msg=no coordinates found, skipping")
                        continue
                    url = f"{source['url']}&latitude={lat}&longitude={lon}"
                    df = read_api(url, source.get("record_path"))
                    df["city"] = canonical_city
                    df = clean(df)
                    load(df, target_table, pk, name)
                    logger.info(f"source={name} city={city} loaded=1")
                except Exception as e:
                    logger.error(f"source={name} city={city} error={e}")
                    continue
            logger.info(f"source={name} cities_processed={len(cities)}")


if __name__ == "__main__":
    main()
