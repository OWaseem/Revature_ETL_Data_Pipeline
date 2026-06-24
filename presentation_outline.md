# Presentation Outline — Data Ingestion Sub-System
**Duration:** 5 minutes | **Slides:** 13

---

## Slide 1: Title Slide

**Title:** Data Ingestion Sub-System — ETL Pipeline

**Subtitle:** Connecting flight delays, hotel availability, and live weather into one unified view

**Name:** Omar Waseem
**Program:** Revature Data Engineering
**Date:** June 2026

---

## Slide 2: Agenda

- Problem Statement
- Solution Overview
- Tech Stack
- Architecture
- Implementation
- Demo
- Challenges & How We Solved Them
- Future Enhancements
- Q&A

---

## Slide 3: Problem Statement

**Picture this:**

Your flight is delayed. You're stuck at an airport in an unfamiliar city with no idea what to do next.

- **Do you wait it out in the terminal?** You don't know if the delay is 2 hours or overnight.
- **Do you leave and find a hotel?** You have no idea what's available nearby or what it costs.
- **Do you step outside?** You have no idea what the weather is like.

**The data gap:**

Flight delay datasets tell you *a flight is delayed* — and nothing else. Hotel availability and weather data exist separately, in completely different formats (CSV, JSON, live APIs), with no standardized way to combine them. There is no single place where a traveler or airline operations team can look up a city and immediately see flight activity, nearby hotel options, and current weather together.

**This pipeline exists to close that gap.**

---

## Slide 4: Solution Overview

**Built a Python ETL pipeline that ingests all three data sources and unifies them into a single city-level view.**

| Source | Format | What it provides |
|--------|--------|-----------------|
| Flight records | CSV | Which flights are arriving, delays, airlines |
| Hotel bookings | JSON | What hotels are available per city, pricing |
| Live weather | Open-Meteo API | Real-time temperature, wind, precipitation |

**How it works:**
- All three sources are extracted, cleaned, validated, and loaded into PostgreSQL staging tables
- A reporting VIEW (`vw_travel_summary`) joins all three into one city-level summary
- A Flask dashboard lets anyone look up any city and instantly see all three data points together

**Result:** One pipeline run processes 4,500+ rows across 98 cities and produces a unified, query-ready dataset — the context a stranded traveler actually needs.

---

## Slide 5: Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3 |
| Data processing | pandas |
| Database driver | psycopg2-binary |
| Configuration | PyYAML (sources.yml) |
| Weather source | Open-Meteo API (free, no key required) |
| Credentials | python-dotenv (.env) |
| Testing | pytest + pytest-cov |
| Dashboard | Flask + Bootstrap 5 + Chart.js |
| Database | PostgreSQL |

**No ORMs** — raw parameterized SQL throughout to prevent SQL injection and maintain full control over UPSERT logic.

---

## Slide 6: Architecture Diagram

```
  CSV (flights.csv)        JSON (hotels.json)        Open-Meteo API
  [flight delays,          [hotel bookings,           [live weather
   airlines, cities]        pricing, cities]           per city coords]
          |                        |                        |
     csv_reader.py           json_reader.py           api_reader.py
     (reads local file)      (reads local file)       (live HTTP request,
                                                        handles network errors)
          \                        |                        /
           \______________________ | ______________________/
                                   |
                              clean.py
                    (strip whitespace, title-case cities,
                     coerce types, drop duplicates)
                                   |
                             validate.py
                    (config-driven rules from sources.yml:
                     null checks, domain rules like delay >= 0)
                                   |
                    _______________|_______________
                   |                               |
              load.py                         load_rejects()
         (UPSERT into stg_*)            (INSERT into stg_rejects)
                   |
    _______________________________________________
    |           |            |          |         |
stg_cities  stg_flights  stg_hotels  stg_weather  stg_rejects
                   |
          vw_travel_summary
    (city | flights | avg delay | hotels | avg price | weather)
                   |
          Flask Dashboard
    (search any city → see all three data points)
```

**How to read this diagram:** Data enters from three different sources at the top, each handled by its own reader. All three converge into the same clean → validate → load pipeline in the middle. Valid rows go into staging tables, invalid rows go into `stg_rejects`. At the bottom, `vw_travel_summary` is a PostgreSQL VIEW that joins all three staging tables into one city-level row — which the Flask dashboard then queries and displays.

**5 staging tables + 1 reporting view + 1 dashboard**

---

## Slide 7: Implementation — Pipeline Design

**Single source of truth:** `config/sources.yml` defines every source — file path, target table, primary key, and validation rules. Adding a new data source requires zero code changes.

**Folder structure:**
```
src/
  readers/       — one reader per source type (csv, json, api)
  clean.py       — normalization layer
  validate.py    — rule engine
  load.py        — UPSERT + FK violation handler
  main.py        — orchestrator
config/
  sources.yml    — all source definitions and rules
data/
  airports.json  — 98 cities, single source of truth for coords, regions, countries
```

**Key design decisions:**
- `airports.json` drives everything — city names, coordinates, regions. No hardcoded lists anywhere in code. Adding a new city means adding one entry to the JSON file.
- Weather coordinates are looked up dynamically from `stg_cities` after airports load — the pipeline figures out what to fetch on its own
- UPSERT (`ON CONFLICT DO UPDATE`) makes every pipeline run idempotent — safe to re-run without duplicates
- Structured logging in `key=value` format for easy parsing and auditing

---

## Slide 8: Implementation — Data Quality & Rejects

**Why data quality matters for this use case:**
A traveler looking up hotels in a city shouldn't get results with a null guest name or a negative price. Bad data needs to be caught before it reaches the reporting layer.

**Validation rules (from sources.yml):**

| Source | Column | Rule |
|--------|--------|------|
| flights | `flight_id` | not null |
| flights | `delay_minutes` | >= 0 |
| hotels | `guest_name` | not null |
| hotels | `price_per_night` | > 0 |
| airports | `city`, `lat`, `lon` | not null |

**Two types of rejects:**
1. **Validation failures** — row breaks a domain rule (e.g. negative delay, null guest name)
2. **FK violations** — `arrival_city` references a city not in `stg_cities`, caught at load time

**Every reject stored in `stg_rejects` with:**
- `source_name` — which source the bad row came from
- `raw_payload` — the full original row as JSON, so it can be reprocessed
- `reason` — the exact rule that failed

**Result:** 4,508 flights + 4,507 hotels + 98 weather records loaded cleanly. Exactly **34 rejects** from intentional dirty rows — no silent data loss.

---

## Slide 9: Live Demo

**Demo flow:**

1. Run: `./run_pipeline.sh` — show structured log output (rows loaded, rejects logged per source)
2. Open Flask dashboard at `http://127.0.0.1:5000`:
   - **Overview page** — stat cards showing 98 cities, 4508 flights, 4507 hotels, 98 weather records, 34 rejects + bar charts
   - **Travel Summary** — pick any city (e.g. Atlanta) and see its flights, average delay, hotel count, average price, and live weather all in one row — this is the core value of the pipeline
   - Click the **Hotels stat card** → filter to Atlanta → see all Atlanta hotel bookings paginated
   - **Rejects page** — filter by source, see exactly which rows failed and why
   - **ERD page** — show the FK relationships that enforce data integrity
3. Run: `./run_tests.sh` — 33 tests passing at 87% coverage

---

## Slide 10: Challenges & How We Solved Them

**Challenge 1: City name casing broke FK integrity**
- `str.title()` in `clean.py` transformed `"Xi'an"` → `"Xi'An"` and `"Rio de Janeiro"` → `"Rio De Janeiro"`, causing every flight/hotel arriving in those cities to fail FK validation
- This produced 171 unexpected FK rejects on top of the 34 expected ones — surfaced only when we queried `stg_rejects` and noticed the count was 205 instead of 34
- **Fix:** Applied the same `str.title()` transformation to the `city` column in airports so `stg_cities` stores the same casing that flight/hotel data produces after cleaning

**Challenge 2: Weather API silently skipping cities**
- Case-sensitive city lookup in `get_city_coords()` meant `"Xi'An"` (from flights after title-casing) didn't match `"Xi'an"` stored in the DB — so weather was never fetched for those cities
- **Fix:** Changed query to `LOWER(city) = LOWER(%s)` and returned the canonical city name from the DB, then used that name when writing to `stg_weather`

**Challenge 3: Connecting three independently formatted sources**
- Flights (CSV), hotels (JSON), and weather (API) have completely different schemas, column names, and structures
- **Fix:** `column_map` in `sources.yml` maps each source's raw column names to a standardized internal schema before any validation or cleaning runs

---

## Slide 11: Future Enhancements

| Area | Plan |
|------|------|
| **Real-world data** | Replace generated data with public flight delay datasets (e.g. FAA/BTS data) to test the pipeline against truly unpredictable input |
| **LLM summary** | After each run, send stats to an LLM and display a plain-English summary on the dashboard: *"Atlanta had the highest average delay at 47 minutes. Hotels there average $182/night with light rain forecast."* |
| **Traveler-facing query** | Add a search bar where a user types a city name and gets a one-page summary — flights, hotels, weather — built directly from `vw_travel_summary` |
| **Scheduled runs** | Use APScheduler to refresh weather data on an interval so the dashboard always shows current conditions |
| **Docker** | `docker compose up` to spin up PostgreSQL + pipeline + dashboard as a single deployable stack |

---

## Slide 12: Conclusion

**The problem:** Flight delay datasets leave travelers with no context — no hotel options, no weather, no way to make a decision.

**What was built:** A pipeline that pulls together all three data sources, enforces data quality at every step, and surfaces a unified city-level view that actually answers the question: *"My flight is delayed in Atlanta — what do I do?"*

**What it demonstrates:**
- Raw data from three different formats becoming one clean, query-ready dataset
- A pipeline that is observable (structured logs), testable (87% coverage, 33 tests), and reproducible (UPSERT + config-driven)
- Real data engineering skills: FK integrity, reject handling, idempotency, API integration

*The same architecture scales to any set of data sources — swap the entries in `sources.yml` and the pipeline handles the rest.*

---

## Slide 13: Q&A

**Thank you!**

*Happy to walk through any part of the code, the database schema, or the dashboard.*

**Repo:** `https://github.com/OWaseem/Revature_ETL_Data_Pipeline`

---

## Presenter Notes — Timing Guide

| Slide | Time |
|-------|------|
| 1 — Title | 15 sec |
| 2 — Agenda | 15 sec |
| 3 — Problem | 40 sec |
| 4 — Solution | 30 sec |
| 5 — Tech Stack | 20 sec |
| 6 — Architecture | 25 sec |
| 7 — Pipeline Design | 25 sec |
| 8 — Data Quality | 25 sec |
| 9 — Demo | 60 sec |
| 10 — Challenges | 30 sec |
| 11 — Future | 15 sec |
| 12 — Conclusion | 20 sec |
| 13 — Q&A | remaining |
