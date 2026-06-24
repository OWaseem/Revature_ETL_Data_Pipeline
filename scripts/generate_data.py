import random
import json
import csv
import math
import os
from datetime import datetime, timedelta

random.seed(42)

with open("data/airports.json") as f:
    airports_data = json.load(f)["airports"]

seen = set()
airports_unique = []
for a in airports_data:
    if a["city"] not in seen:
        airports_unique.append(a)
        seen.add(a["city"])

CITIES = [a["city"] for a in airports_unique]
CITY_COORDS = {a["city"]: (a["lat"], a["lon"]) for a in airports_unique}
CITY_REGION = {a["city"]: a["region"] for a in airports_unique}
CITY_COUNTRY = {a["city"]: a["country"] for a in airports_unique}

# maps airline to the country codes it is based in
AIRLINE_COUNTRIES = {
    "Delta": ["US"],
    "American Airlines": ["US"],
    "United Airlines": ["US"],
    "Air Canada": ["CA"],
    "AeroMexico": ["MX"],
    "LATAM Airlines": ["BR", "CL", "PE", "CO", "AR"],
    "Avianca": ["CO"],
    "British Airways": ["GB"],
    "Air France": ["FR"],
    "Lufthansa": ["DE"],
    "KLM": ["NL"],
    "Iberia": ["ES"],
    "Turkish Airlines": ["TR"],
    "Emirates": ["AE"],
    "Ethiopian Airlines": ["ET"],
    "Air India": ["IN"],
    "Pakistan International": ["PK"],
    "Japan Airlines": ["JP"],
    "Korean Air": ["KR"],
    "Cathay Pacific": ["HK"],
    "Singapore Airlines": ["SG"],
    "Thai Airways": ["TH"],
    "Qantas": ["AU"],
}

# fallback pool when neither city has a local airline
REGION_AIRLINES = {
    "north_america": ["Delta", "American Airlines", "United Airlines", "Air Canada"],
    "south_america": ["LATAM Airlines", "Avianca", "AeroMexico"],
    "europe": ["British Airways", "Air France", "Lufthansa", "KLM", "Iberia", "Turkish Airlines"],
    "middle_east": ["Emirates", "Turkish Airlines"],
    "africa": ["Ethiopian Airlines", "Emirates"],
    "south_asia": ["Air India", "Pakistan International", "Emirates"],
    "east_asia": ["Japan Airlines", "Korean Air", "Cathay Pacific"],
    "southeast_asia": ["Singapore Airlines", "Thai Airways", "Cathay Pacific"],
    "oceania": ["Qantas", "Singapore Airlines"],
    "central_asia": ["Turkish Airlines", "Lufthansa"],
}

GLOBAL_AIRLINES = ["Emirates", "Turkish Airlines", "Singapore Airlines", "Lufthansa", "British Airways"]

REGION_PRICE_RANGE = {
    "north_america": (150, 600),
    "south_america": (80, 300),
    "europe": (120, 700),
    "middle_east": (200, 800),
    "africa": (60, 200),
    "south_asia": (40, 250),
    "east_asia": (100, 550),
    "southeast_asia": (70, 450),
    "oceania": (150, 600),
    "central_asia": (50, 180),
}

HOTEL_BRANDS = ["Grand", "Hilton", "Marriott", "Hyatt", "Sheraton", "Sofitel", "Radisson", "Four Seasons"]

GUEST_NAMES = [
    "James Smith", "Sarah Johnson", "Marie Dupont", "Yuki Tanaka",
    "Carlos Rivera", "Emma Brown", "David Chen", "Aiko Sato",
    "John Williams", "Anna Müller", "Mohammed Al Rashid", "Li Wei",
    "Sophie Martin", "Raj Patel", "Elena Kozlov", "Omar Hassan",
    "Fatima Al Zahra", "Lucas Oliveira", "Amara Diallo", "Priya Sharma",
    "Hiroshi Yamamoto", "Isabella Rossi", "Ahmed Hassan", "Mei Lin",
    "Diego Hernandez", "Olga Petrov", "Kwame Mensah", "Nadia Johansson"
]


def get_hotels_for_city(city):
    return [f"{brand} {city}" for brand in HOTEL_BRANDS]


def get_airline_for_route(dep_city, arr_city):
    dep_country = CITY_COUNTRY.get(dep_city)
    arr_country = CITY_COUNTRY.get(arr_city)

    country_airlines = [
        airline for airline, countries in AIRLINE_COUNTRIES.items()
        if dep_country in countries or arr_country in countries
    ]

    if country_airlines:
        candidates = list(set(country_airlines + GLOBAL_AIRLINES))
    else:
        dep_region = CITY_REGION.get(dep_city, "europe")
        arr_region = CITY_REGION.get(arr_city, "europe")
        candidates = list(set(
            REGION_AIRLINES.get(dep_region, []) +
            REGION_AIRLINES.get(arr_region, []) +
            GLOBAL_AIRLINES
        ))

    return random.choice(candidates)


def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def flight_duration_hours(dep_city, arr_city):
    lat1, lon1 = CITY_COORDS[dep_city]
    lat2, lon2 = CITY_COORDS[arr_city]
    distance_km = haversine(lat1, lon1, lat2, lon2)
    return max(1.0, distance_km / 850 + random.uniform(0.25, 1.0))


def get_hotel_price(city):
    region = CITY_REGION.get(city, "europe")
    lo, hi = REGION_PRICE_RANGE.get(region, (100, 500))
    return round(random.uniform(lo, hi), 2)


def random_date(start, days):
    return start + timedelta(days=random.randint(0, days))


def generate_flights(n=4500):
    rows = []
    start = datetime(2026, 1, 1, 0, 0)

    for i in range(1, n + 1):
        dep_city = random.choice(CITIES)
        arr_city = random.choice([c for c in CITIES if c != dep_city])
        dep_time = random_date(start, 180) + timedelta(hours=random.randint(0, 23))
        duration = flight_duration_hours(dep_city, arr_city)
        arr_time = dep_time + timedelta(hours=duration)
        delay = random.randint(0, 180)
        airline = get_airline_for_route(dep_city, arr_city)

        rows.append({
            "flight_id": f"FL{i:05d}",
            "departure_city": dep_city,
            "arrival_city": arr_city,
            "departure_time": dep_time.strftime("%Y-%m-%d %H:%M"),
            "arrival_time": arr_time.strftime("%Y-%m-%d %H:%M"),
            "delay_minutes": delay,
            "airline": airline,
        })

    dirty = [
        {"flight_id": "FL99001", "departure_city": "London", "arrival_city": "Dubai", "departure_time": "2026-03-01 08:00", "arrival_time": "2026-03-01 14:00", "delay_minutes": -5, "airline": "Emirates"},
        {"flight_id": "FL99002", "departure_city": "Paris", "arrival_city": None, "departure_time": "2026-03-01 09:00", "arrival_time": "2026-03-01 13:00", "delay_minutes": 10, "airline": "Air France"},
        {"flight_id": "FL99003", "departure_city": None, "arrival_city": "Tokyo", "departure_time": "2026-03-01 10:00", "arrival_time": "2026-03-02 06:00", "delay_minutes": 0, "airline": "Japan Airlines"},
        {"flight_id": "FL99004", "departure_city": "  new york  ", "arrival_city": "  LONDON  ", "departure_time": "2026-03-01 07:00", "arrival_time": "2026-03-01 19:00", "delay_minutes": 30, "airline": "  Delta  "},
        {"flight_id": "FL99005", "departure_city": "Dubai", "arrival_city": "Singapore", "departure_time": "2026-03-02 06:00", "arrival_time": "2026-03-02 13:00", "delay_minutes": 0, "airline": "Emirates"},
        {"flight_id": "FL99005", "departure_city": "Dubai", "arrival_city": "Singapore", "departure_time": "2026-03-02 06:00", "arrival_time": "2026-03-02 13:00", "delay_minutes": 0, "airline": "Emirates"},
        {"flight_id": None, "departure_city": "Bangkok", "arrival_city": "Sydney", "departure_time": "2026-03-03 11:00", "arrival_time": "2026-03-03 22:00", "delay_minutes": 15, "airline": "Thai Airways"},
        {"flight_id": "FL99007", "departure_city": "Amsterdam", "arrival_city": "Frankfurt", "departure_time": "2026-03-04 08:00", "arrival_time": "2026-03-04 09:30", "delay_minutes": "unknown", "airline": "KLM"},
        {"flight_id": "FL99008", "departure_city": "Moscow", "arrival_city": "Doha", "departure_time": "2026-03-05 06:00", "arrival_time": "2026-03-05 10:00", "delay_minutes": -999, "airline": "Turkish Airlines"},
        {"flight_id": "FL99009", "departure_city": "Cairo", "arrival_city": "Nairobi", "departure_time": "2026-03-06 08:00", "arrival_time": "2026-03-06 12:00", "delay_minutes": 20, "airline": None},
        {"flight_id": "FL99010", "departure_city": "Mumbai", "arrival_city": "Dubai", "departure_time": "2026-03-07 09:00", "arrival_time": "2026-03-07 11:00", "delay_minutes": 5, "airline": "   "},
        {"flight_id": "FL99011", "departure_city": "Sydney", "arrival_city": "Melbourne", "departure_time": None, "arrival_time": "2026-03-08 10:00", "delay_minutes": 0, "airline": "Qantas"},
        {"flight_id": "FL99012", "departure_city": "Toronto", "arrival_city": "Montreal", "departure_time": "2026-03-09 07:00", "arrival_time": "2026-03-09 08:30", "delay_minutes": -20, "airline": "Air Canada"},
        {"flight_id": "FL99013", "departure_city": "  SEOUL  ", "arrival_city": "  taipei  ", "departure_time": "2026-03-10 10:00", "arrival_time": "2026-03-10 12:00", "delay_minutes": 10, "airline": "  korean AIR  "},
        {"flight_id": None, "departure_city": None, "arrival_city": None, "departure_time": None, "arrival_time": None, "delay_minutes": None, "airline": None},
        {"flight_id": "FL99015", "departure_city": "Vienna", "arrival_city": "Prague", "departure_time": "2026-03-11 06:00", "arrival_time": "2026-03-11 07:00", "delay_minutes": -100, "airline": "Lufthansa"},
        {"flight_id": "FL99016", "departure_city": "Zurich", "arrival_city": "Brussels", "departure_time": "not-a-date", "arrival_time": "also-not-a-date", "delay_minutes": 15, "airline": "KLM"},
        {"flight_id": "FL99017", "departure_city": "São Paulo", "arrival_city": "Buenos Aires", "departure_time": "2026-03-12 08:00", "arrival_time": "2026-03-12 11:00", "delay_minutes": 0, "airline": "LATAM Airlines"},
        {"flight_id": "FL99018", "departure_city": "Bogotá", "arrival_city": "Lima", "departure_time": "2026-03-13 09:00", "arrival_time": "2026-03-13 11:00", "delay_minutes": 0, "airline": "Avianca"},
        {"flight_id": "", "departure_city": "Johannesburg", "arrival_city": "Nairobi", "departure_time": "2026-03-14 07:00", "arrival_time": "2026-03-14 10:00", "delay_minutes": 30, "airline": "Ethiopian Airlines"},
        {"flight_id": "FL99020", "departure_city": "Riyadh", "arrival_city": "Jeddah", "departure_time": "2026-03-15 08:00", "arrival_time": "2026-03-15 09:00", "delay_minutes": 5, "airline": "A" * 200},
        {"flight_id": "FL99021", "departure_city": "Doha", "arrival_city": "Kuwait City", "departure_time": "2026-03-16 10:00", "arrival_time": "2026-03-16 11:00", "delay_minutes": -1, "airline": "Emirates"},
        {"flight_id": "FL99022", "departure_city": "Muscat", "arrival_city": None, "departure_time": "2026-03-17 06:00", "arrival_time": "2026-03-17 08:00", "delay_minutes": 10, "airline": "Oman Air"},
        {"flight_id": "FL99023", "departure_city": None, "arrival_city": "Abu Dhabi", "departure_time": "2026-03-18 07:00", "arrival_time": "2026-03-18 09:00", "delay_minutes": 0, "airline": "Etihad"},
        {"flight_id": "FL99024", "departure_city": "Tel Aviv", "arrival_city": "Istanbul", "departure_time": "2026-03-19 08:00", "arrival_time": "2026-03-19 10:00", "delay_minutes": -30, "airline": "Turkish Airlines"},
        {"flight_id": "FL99025", "departure_city": "Dublin", "arrival_city": "Manchester", "departure_time": "2026-03-20 07:00", "arrival_time": "2026-03-20 08:00", "delay_minutes": 5, "airline": "British Airways"},
        {"flight_id": "FL99025", "departure_city": "Dublin", "arrival_city": "Manchester", "departure_time": "2026-03-20 07:00", "arrival_time": "2026-03-20 08:00", "delay_minutes": 5, "airline": "British Airways"},
    ]

    rows.extend(dirty)
    random.shuffle(rows)
    return rows


def generate_hotels(n=4500):
    records = []
    start = datetime(2026, 1, 1)

    for i in range(1, n + 1):
        city = random.choice(CITIES)
        hotel = random.choice(get_hotels_for_city(city))
        check_in = random_date(start, 180)
        check_out = check_in + timedelta(days=random.randint(1, 14))
        guest = random.choice(GUEST_NAMES)
        price = get_hotel_price(city)

        records.append({
            "hotel_id": f"H{i:05d}",
            "hotel_name": hotel,
            "arrival_city": city,
            "check_in": check_in.strftime("%Y-%m-%d"),
            "check_out": check_out.strftime("%Y-%m-%d"),
            "guest_name": guest,
            "price_per_night": price,
        })

    dirty = [
        {"hotel_id": "H99001", "hotel_name": "The Savoy", "arrival_city": "London", "check_in": "2026-03-01", "check_out": "2026-03-05", "guest_name": None, "price_per_night": 480},
        {"hotel_id": "H99002", "hotel_name": "Burj Al Arab", "arrival_city": "Dubai", "check_in": "2026-03-01", "check_out": "2026-03-03", "guest_name": "Test User", "price_per_night": -100},
        {"hotel_id": "H99003", "hotel_name": "The Plaza", "arrival_city": "New York", "check_in": "2026-03-01", "check_out": "2026-03-02", "guest_name": "Jane Doe", "price_per_night": 0},
        {"hotel_id": "H99004", "hotel_name": "Park Hyatt Tokyo", "arrival_city": "  TOKYO  ", "check_in": "2026-03-02", "check_out": "2026-03-04", "guest_name": "  John Doe  ", "price_per_night": 350},
        {"hotel_id": "H99005", "hotel_name": "Raffles Hotel", "arrival_city": None, "check_in": "2026-03-03", "check_out": "2026-03-06", "guest_name": "Alice Wong", "price_per_night": 500},
        {"hotel_id": "H99006", "hotel_name": "Mandarin Oriental Bangkok", "arrival_city": "Bangkok", "check_in": "2026-03-04", "check_out": "2026-03-07", "guest_name": "Bob Lee", "price_per_night": 220},
        {"hotel_id": "H99006", "hotel_name": "Mandarin Oriental Bangkok", "arrival_city": "Bangkok", "check_in": "2026-03-04", "check_out": "2026-03-07", "guest_name": "Bob Lee", "price_per_night": 220},
        {"hotel_id": "H99007", "hotel_name": "W Amsterdam", "arrival_city": "Amsterdam", "check_in": None, "check_out": "2026-03-10", "guest_name": "Clara Schmidt", "price_per_night": 310},
        {"hotel_id": "H99008", "hotel_name": "Four Seasons Singapore", "arrival_city": "Singapore", "check_in": "2026-03-05", "check_out": None, "guest_name": "Wei Chen", "price_per_night": 420},
        {"hotel_id": "H99009", "hotel_name": "Grand Hyatt São Paulo", "arrival_city": "São Paulo", "check_in": "2026-03-06", "check_out": "2026-03-08", "guest_name": "Lucas Oliveira", "price_per_night": -500},
        {"hotel_id": "H99010", "hotel_name": "Some Hotel", "arrival_city": None, "check_in": "2026-03-07", "check_out": "2026-03-09", "guest_name": None, "price_per_night": 200},
        {"hotel_id": "H99011", "hotel_name": "The Ritz Moscow", "arrival_city": "Moscow", "check_in": "2026-03-08", "check_out": "2026-03-10", "guest_name": "   ", "price_per_night": 380},
        {"hotel_id": "H99012", "hotel_name": "Alvear Palace Hotel", "arrival_city": "Buenos Aires", "check_in": "2026-03-09", "check_out": "2026-03-11", "guest_name": "Diego Hernandez", "price_per_night": 0},
        {"hotel_id": "H99013", "hotel_name": "Sheraton Addis", "arrival_city": "Addis Ababa", "check_in": "not-a-date", "check_out": "2026-03-12", "guest_name": "Amara Diallo", "price_per_night": 150},
        {"hotel_id": "H99014", "hotel_name": "The Oberoi New Delhi", "arrival_city": "New Delhi", "check_in": "2026-03-10", "check_out": "2026-03-12", "guest_name": "Priya Sharma", "price_per_night": -10},
        {"hotel_id": "H99015", "hotel_name": None, "arrival_city": "Nairobi", "check_in": "2026-03-11", "check_out": "2026-03-13", "guest_name": "Kwame Mensah", "price_per_night": 180},
        {"hotel_id": "H99016", "hotel_name": "Four Seasons Vienna", "arrival_city": "Vienna", "check_in": "2026-03-12", "check_out": "2026-03-14", "guest_name": "Anna Müller", "price_per_night": 520},
        {"hotel_id": "H99016", "hotel_name": "Four Seasons Vienna", "arrival_city": "Vienna", "check_in": "2026-03-12", "check_out": "2026-03-14", "guest_name": "Anna Müller", "price_per_night": 520},
        {"hotel_id": "H99017", "hotel_name": "Baur au Lac", "arrival_city": "  ZURICH  ", "check_in": "2026-03-13", "check_out": "2026-03-15", "guest_name": "Sophie Martin", "price_per_night": 890},
        {"hotel_id": "H99018", "hotel_name": "Bairro Alto Hotel", "arrival_city": "Lisbon", "check_in": None, "check_out": "2026-03-16", "guest_name": None, "price_per_night": 310},
        {"hotel_id": "H99019", "hotel_name": "Grand Hotel Oslo", "arrival_city": "Oslo", "check_in": "2026-03-14", "check_out": "2026-03-16", "guest_name": "Nadia Johansson", "price_per_night": 0},
        {"hotel_id": "H99020", "hotel_name": "Hotel d'Angleterre", "arrival_city": "Copenhagen", "check_in": "2026-03-15", "check_out": "2026-03-17", "guest_name": "Emma Brown", "price_per_night": -250},
        {"hotel_id": "H99021", "hotel_name": "At Six Stockholm", "arrival_city": None, "check_in": "2026-03-16", "check_out": "2026-03-18", "guest_name": "Olga Petrov", "price_per_night": 430},
        {"hotel_id": "H99022", "hotel_name": "Hotel Kämp Helsinki", "arrival_city": "Helsinki", "check_in": "2026-03-17", "check_out": "2026-03-19", "guest_name": None, "price_per_night": 360},
        {"hotel_id": "H99023", "hotel_name": "Raffles Makati", "arrival_city": "Manila", "check_in": "2026-03-18", "check_out": "2026-03-20", "guest_name": "  ", "price_per_night": 280},
        {"hotel_id": "H99024", "hotel_name": "W Brisbane", "arrival_city": "Brisbane", "check_in": "2026-03-19", "check_out": "2026-03-21", "guest_name": "James Smith", "price_per_night": 0},
    ]

    records.extend(dirty)
    random.shuffle(records)
    return records


if __name__ == "__main__":
    flights_path = "data/flights.csv"
    hotels_path = "data/hotels.json"
    min_rows = 4500

    if os.path.exists(flights_path):
        with open(flights_path) as f:
            existing = sum(1 for _ in f) - 1
        if existing >= min_rows:
            print(f"flights.csv already has {existing} rows — skipping generation")
        else:
            flights = generate_flights()
            with open(flights_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["flight_id", "departure_city", "arrival_city",
                                                        "departure_time", "arrival_time", "delay_minutes", "airline"])
                writer.writeheader()
                writer.writerows(flights)
            print(f"Generated {len(flights)} flight rows")
    else:
        flights = generate_flights()
        with open(flights_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["flight_id", "departure_city", "arrival_city",
                                                    "departure_time", "arrival_time", "delay_minutes", "airline"])
            writer.writeheader()
            writer.writerows(flights)
        print(f"Generated {len(flights)} flight rows")

    if os.path.exists(hotels_path):
        with open(hotels_path) as f:
            existing = len(json.load(f).get("hotels", []))
        if existing >= min_rows:
            print(f"hotels.json already has {existing} rows — skipping generation")
        else:
            hotels = generate_hotels()
            with open(hotels_path, "w") as f:
                json.dump({"hotels": hotels}, f, indent=2)
            print(f"Generated {len(hotels)} hotel rows")
    else:
        hotels = generate_hotels()
        with open(hotels_path, "w") as f:
            json.dump({"hotels": hotels}, f, indent=2)
        print(f"Generated {len(hotels)} hotel rows")
