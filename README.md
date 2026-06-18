# Revature ETL Data Pipeline

A data ingestion pipeline that extracts data from CSV, JSON, and API sources, validates and cleans it, then loads it into PostgreSQL staging tables.

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
    airports.json
    ai_student_impact_dataset.csv
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
| airports | JSON | data/airports.json |
| ai_student | CSV | data/ai_student_impact_dataset.csv |
| dad_jokes | API | https://icanhazdadjoke.com/search |

---

## PostgreSQL Staging Tables
- `stg_customers` — customer records
- `stg_sales` — sales transactions
- `stg_rejects` — rejected rows with reason and raw payload

---

## Validation Rules
| Source | Rule |
|--------|------|
| airports | `lat`/`lon` must be numeric |
| airports | `country` must be exactly 2 characters |
| ai_student | `Pre_Semester_GPA` and `Post_Semester_GPA` must be >= 0 |
| dad_jokes | `joke` must not be an empty string |

---

## Game Plan — Progress Tracker
- [x] Step 1: requirements.txt
- [x] Step 2: PostgreSQL database + staging tables
- [x] Step 3: Reader layer (csv, json, api)
- [x] Step 4: config.py + sources.yml
- [x] Step 5: main.py (orchestration skeleton)
- [ ] Step 6: rules.py + validate.py
- [ ] Step 7: clean.py
- [ ] Step 8: load.py (psycopg2 UPSERT)
- [ ] Step 9: .env + database connection
- [ ] Step 10: tests (80%+ coverage)
- [ ] Step 11: Real-world unclean datasets
- [ ] Step 12: Flask dashboard (visualize pipeline + cleaned tables)

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
