# Revature ETL Data Pipeline

A transportation data pipeline that extracts flight, hotel, and live weather data, validates and cleans it, then loads it into PostgreSQL staging tables — with a Flask dashboard for visualization.

---

## Tech Stack
- **Language:** Python 3
- **Database:** PostgreSQL
- **Libraries:** pandas, psycopg2-binary, pyyaml, python-dotenv, requests, pytest, pytest-cov, flask

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
  scripts/
    generate_data.py   # generates 4500+ flight and hotel rows with intentional dirty data
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
    test_clean.py
    test_config.py
    test_load.py
    test_log.py
    test_main.py
  dashboard/
    app.py             # Flask app with 4 routes
    templates/
      base.html        # shared layout: dark navbar, active link highlighting, reject badge, footer
      overview.html    # pipeline stats + Chart.js bar charts (rows loaded, rejects by source)
      travel.html      # vw_travel_summary table with city count badge
      rejects.html     # rejected rows with live search/filter by source
      erd.html         # DBeaver ERD screenshot
    static/
      erd.png          # exported ERD from DBeaver
  run_pipeline.sh      # runs src/main.py
  run_tests.sh         # runs pytest with coverage
  generate_data.sh     # runs scripts/generate_data.py
  run_dashboard.sh     # runs dashboard/app.py
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
Clean Layer        — strips whitespace, normalizes casing, fixes data types, applies column_map
    ↓
Validation Layer   — checks nulls, types, domain rules (config-driven via sources.yml)
    ↓
Load Layer         — batch UPSERT into PostgreSQL staging tables
                   — FK violations caught and logged to stg_rejects
    ↓
Rejects Table      — bad rows saved to stg_rejects with source name and reason
    ↓
Reporting View     — vw_travel_summary joins all three sources into a city-level summary
    ↓
Flask Dashboard    — visualizes pipeline stats, travel summary, rejects, and ERD
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
Weather API coordinates are looked up dynamically from `stg_cities` based on unique `arrival_city` values from flights.

**Cities in use:** 98 major international cities spanning North America, South America, Europe, Middle East, Africa, South Asia, East Asia, Southeast Asia, Oceania, and Central Asia. City region data is read directly from `airports.json` — no hardcoded mappings in code.

---

## PostgreSQL Staging Tables
- `stg_cities` — reference table of airports/cities (primary key: `city`, includes `region` field)
- `stg_flights` — cleaned flight records (FK: `arrival_city` → `stg_cities.city`)
- `stg_hotels` — cleaned hotel bookings (FK: `arrival_city` → `stg_cities.city`)
- `stg_weather` — live weather at arrival cities (FK: `city` → `stg_cities.city`)
- `stg_rejects` — rejected rows with reason, source name, and raw payload

## Reporting View
- `vw_travel_summary` — city-level summary joining all three sources:
  - `total_flights` — number of flights arriving per city
  - `avg_delay_minutes` — average flight delay per city
  - `total_hotels` — number of hotel bookings per city
  - `avg_price_per_night` — average hotel price per city
  - `temperature_2m`, `wind_speed_10m`, `precipitation` — live weather per city

---

## Flask Dashboard
Six pages accessible from a dark navbar with active link highlighting and a live rejects badge:

| Page | URL | Content |
|------|-----|---------|
| Overview | `/` | Stat cards (cities, flights, hotels, weather, rejects) + Chart.js bar charts |
| Travel Summary | `/travel` | vw_travel_summary table with city count badge |
| Rejects | `/rejects` | Rejected rows with search box and source dropdown filter |
| ERD | `/erd` | DBeaver entity-relationship diagram |
| Table View | `/table/<name>` | Staging table data — cities, flights, hotels, or weather |

Stat cards on the Overview page are clickable and link directly to their respective staging table. Large tables (flights, hotels) show the first 100 rows with a "Showing 100 of N" badge. All table views include a live search box.

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
- [x] Step 7: clean.py (column_map support for real-world datasets)
- [x] Step 8: load.py (psycopg2 UPSERT + FK violation handling)
- [x] Step 9: .env + database connection
- [x] Step 10: Wire up main.py fully
- [x] Step 10b: stg_cities + FK relationships + ERD in DBeaver
- [x] Step 11: structured logging (key=value format via Python logging module)
- [x] Step 12: tests (87% coverage — 33 tests across validate, clean, load, config, log, main)
- [x] Step 13: generate_data.py — 4500+ rows with 50 intentional dirty rows across 98 cities; cities, regions, and airline routes derived dynamically from airports.json
- [x] Step 13b: vw_travel_summary — reporting view joining flights, hotels, and weather
- [x] Step 14: Flask dashboard — 4-page app with Chart.js charts, reject badge, search/filter on rejects, city count badge on travel summary
- [ ] Step 15: Real-world unclean datasets (hospital records, music, etc.)

---

## Running the Project
```bash
# Generate data (only needed once)
./generate_data.sh

# Run the pipeline
./run_pipeline.sh

# Run tests with coverage
./run_tests.sh

# Launch the dashboard (http://127.0.0.1:5000)
./run_dashboard.sh
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
TEST_DB_NAME=test_ingest_db
```
