rules = {
    "flights": [
        {"column": "flight_id", "condition": "value is not None"},
        {"column": "arrival_city", "condition": "value is not None"},
        {"column": "delay_minutes", "condition": "value >= 0"}
    ],

    "hotels": [
        {"column": "guest_name", "condition": "value is not None"},
        {"column": "price_per_night", "condition": "value > 0"}
    ]
}
