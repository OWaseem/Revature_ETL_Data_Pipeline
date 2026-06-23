# Revature ETL Data Pipeline

A transportation data pipeline that extracts flight, hotel, and live weather data, validates and cleans it, then loads it into PostgreSQL staging tables.

---

## Tech Stack
- **Language:** Python 3
- **Database:** PostgreSQL
- **Libraries:** pandas, psycopg2-binary, pyyaml, python-dotenv, requests, pytest, pytest-cov

---

## Project Structure
```
Revature_ETL_Data_Pipeline/
  config/
    sources.yml        # defines all data sources and validation rules
  data/
    flights.csv        # flight records (pipeline source)
    hotels.json        # hotel bookings (pipeline source)
    airports.json      # reference data: city coords and airport info (pipeline source → stg_cities)
  src/
    config.py          # loads sources.yml
    readers/
      csv_reader.py    # reads CSV → DataFrame
      json_reader.py   # reads JSON → DataFrame
      api_reader.py    # fetches API → DataFrame
    validate.py        # checks nulls, types, domain rules
    clean.py           # strips whitespace, title-cases cities, fixes types, drops duplicates
    load.py            # batch UPSERT into PostgreSQL, FK violations logged to stg_rejects
    log.py             # configures structured logger (key=value format)
    main.py            # orchestrates the full pipeline
  tests/
    test_validate.py
    test_load.py
  requirements.txt
  .env                 # database credentials (never commit this)
```

---

## Data Flow
```
Source (CSV / JSON / API)
    ↓
Reader Layer       — reads data into a pandas DataFrame
    ↓
Clean Layer        — strips whitespace, normalizes casing, fixes data types
    ↓
Validation Layer   — checks nulls, types, domain rules (config-driven via sources.yml)
    ↓
Load Layer         — batch UPSERT into PostgreSQL staging tables
                   — FK violations caught and logged to stg_rejects
    ↓
Rejects Table      — bad rows saved to stg_rejects with source name and reason
```

---

## Data Sources
| Name | Format | Location |
|------|--------|----------|
| airports | JSON | data/airports.json |
| flights | CSV | data/flights.csv |
| hotels | JSON | data/hotels.json |
| weather | API | Open-Meteo (https://api.open-meteo.com) |

**Note:** Airports is loaded first to populate `stg_cities` before FK-referencing tables.
Weather API coordinates are looked up dynamically from `airports.json` based on `arrival_city` from each flight.

**Cities in use:** Dubai, Tokyo, London, New York, Paris

---

## PostgreSQL Staging Tables
- `stg_cities` — reference table of airports/cities (primary key: `city`)
- `stg_flights` — cleaned flight records (FK: `arrival_city` → `stg_cities.city`)
- `stg_hotels` — cleaned hotel bookings (FK: `arrival_city` → `stg_cities.city`)
- `stg_weather` — live weather at arrival cities (FK: `city` → `stg_cities.city`)
- `stg_rejects` — rejected rows with reason, source name, and raw payload

---

## Validation Rules
| Source | Column | Rule |
|--------|--------|------|
| airports | `city` | must not be null |
| airports | `code` | must not be null |
| airports | `country` | must not be null |
| airports | `lat` | must not be null |
| airports | `lon` | must not be null |
| flights | `flight_id` | must not be null |
| flights | `arrival_city` | must not be null |
| flights | `departure_city` | must not be null |
| flights | `delay_minutes` | must be >= 0 |
| hotels | `guest_name` | must not be null |
| hotels | `arrival_city` | must not be null |
| hotels | `check_in` | must not be null |
| hotels | `check_out` | must not be null |
| hotels | `price_per_night` | must be > 0 |

---

## Game Plan — Progress Tracker
- [x] Step 1: requirements.txt
- [x] Step 2: PostgreSQL database + staging tables
- [x] Step 3: Reader layer (csv, json, api)
- [x] Step 4: config.py + sources.yml
- [x] Step 5: main.py (orchestration skeleton)
- [x] Step 6: validate.py (config-driven rules via sources.yml)
- [x] Step 7: clean.py
- [x] Step 8: load.py (psycopg2 UPSERT + FK violation handling)
- [x] Step 9: .env + database connection
- [x] Step 10: Wire up main.py fully
- [x] Step 10b: stg_cities + FK relationships + ERD in DBeaver
- [x] Step 11: structured logging (key=value format via Python logging module)
- [x] Step 12: tests (87% coverage — 33 tests across validate, clean, load, config, log, main)
- [ ] Step 13: Real-world unclean datasets
- [ ] Step 14: Flask dashboard (visualize pipeline + cleaned tables)

---

## Running the Pipeline
```bash
# From the project root
python3 src/main.py
```

---

## Environment Variables
Create a `.env` file in the project root:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ingest_db
DB_USER=your_username
DB_PASSWORD=your_password
```
