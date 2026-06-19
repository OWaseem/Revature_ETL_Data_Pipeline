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
    sources.yml        # defines all data sources
  data/
    flights.csv        # flight records (pipeline source)
    hotels.json        # hotel bookings (pipeline source)
    airports.json      # lat/lon lookup table (not a pipeline source)
  src/
    config.py          # loads sources.yml
    readers/
      csv_reader.py    # reads CSV → DataFrame
      json_reader.py   # reads JSON → DataFrame
      api_reader.py    # fetches API → DataFrame
    validate.py        # checks nulls, types, domain rules
    rules.py           # validation rule definitions
    clean.py           # fixes/drops bad rows, normalizes columns
    load.py            # batch UPSERT into PostgreSQL
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
Validation Layer   — checks nulls, data types, domain rules
    ↓
Cleaning Layer     — fixes/drops bad rows, normalizes column names
    ↓
Load Layer         — batch UPSERT into PostgreSQL staging tables
    ↓
Rejects Table      — bad rows saved to stg_rejects with a reason
```

---

## Data Sources
| Name | Format | Location |
|------|--------|----------|
| flights | CSV | data/flights.csv |
| hotels | JSON | data/hotels.json |
| weather | API | https://api.open-meteo.com/v1/forecast?current=temperature_2m,weather_code,wind_speed_10m,precipitation |

**Note:** Weather API coordinates are looked up dynamically from `airports.json` based on `arrival_city` from each flight.

**Cities in use:** Dubai, Tokyo, London, New York, Paris

---

## PostgreSQL Staging Tables
- `stg_flights` — cleaned flight records
- `stg_hotels` — cleaned hotel bookings
- `stg_weather` — live weather at arrival cities
- `stg_rejects` — rejected rows with reason and raw payload

---

## Validation Rules
| Source | Column | Rule |
|--------|--------|------|
| flights | `flight_id` | must not be null |
| flights | `arrival_city` | must not be null |
| flights | `delay_minutes` | must be >= 0 |
| hotels | `guest_name` | must not be null |
| hotels | `price_per_night` | must be > 0 |

---

## Game Plan — Progress Tracker
- [x] Step 1: requirements.txt
- [x] Step 2: PostgreSQL database + staging tables
- [x] Step 3: Reader layer (csv, json, api)
- [x] Step 4: config.py + sources.yml
- [x] Step 5: main.py (orchestration skeleton)
- [x] Step 6: rules.py + validate.py
- [ ] Step 7: clean.py
- [ ] Step 8: load.py (psycopg2 UPSERT)
- [ ] Step 9: .env + database connection
- [ ] Step 10: Wire up main.py fully
- [ ] Step 11: tests (80%+ coverage)
- [ ] Step 12: Real-world unclean datasets
- [ ] Step 13: Flask dashboard (visualize pipeline + cleaned tables)

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
