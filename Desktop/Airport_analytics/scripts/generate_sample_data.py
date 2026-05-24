"""
Generates realistic synthetic CSV data for the airport wait time project.
Run this once to populate data/raw/ before running the rest of the pipeline.
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

SEED = 42
np.random.seed(SEED)

RAW_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
os.makedirs(RAW_DIR, exist_ok=True)

# ── Date range: 90 days ───────────────────────────────────────────────────────
START_DATE = datetime(2024, 1, 1)
NUM_DAYS = 90
dates = [START_DATE + timedelta(days=i) for i in range(NUM_DAYS)]

# ── 1. flights.csv ────────────────────────────────────────────────────────────
# ~20 flights per day across 4 airlines and 6 terminals
airlines = ['Delta', 'United', 'Southwest', 'American']
terminals = ['A', 'B', 'C', 'D', 'E', 'F']

flight_rows = []
flight_id = 1
for date in dates:
    num_flights = np.random.randint(15, 26)
    for _ in range(num_flights):
        hour = np.random.randint(5, 23)
        minute = np.random.choice([0, 15, 30, 45])
        scheduled_time = date.replace(hour=hour, minute=minute)
        delay_minutes = int(np.clip(np.random.exponential(15), 0, 180))
        flight_rows.append({
            'flight_id': flight_id,
            'date': date.strftime('%Y-%m-%d'),
            'airline': np.random.choice(airlines),
            'terminal': np.random.choice(terminals),
            'scheduled_departure': scheduled_time.strftime('%H:%M'),
            'delay_minutes': delay_minutes,
            'flight_status': 'Delayed' if delay_minutes > 15 else 'On Time',
        })
        flight_id += 1

flights_df = pd.DataFrame(flight_rows)
flights_df.to_csv(os.path.join(RAW_DIR, 'flights.csv'), index=False)
print(f"flights.csv: {len(flights_df)} rows")

# ── 2. weather.csv ────────────────────────────────────────────────────────────
# One weather record per day
weather_conditions = ['Clear', 'Cloudy', 'Rain', 'Snow', 'Fog', 'Thunderstorm']
weather_weights   = [0.40,    0.25,    0.15,   0.08,   0.07,  0.05]

weather_rows = []
for date in dates:
    condition = np.random.choice(weather_conditions, p=weather_weights)
    temp_f = round(float(np.random.normal(60, 18)), 1)
    wind_mph = round(float(np.clip(np.random.exponential(10), 0, 60)), 1)
    visibility_miles = round(float(np.clip(np.random.normal(8, 3), 0.5, 10)), 1)
    weather_rows.append({
        'date': date.strftime('%Y-%m-%d'),
        'condition': condition,
        'temperature_f': temp_f,
        'wind_speed_mph': wind_mph,
        'visibility_miles': visibility_miles,
    })

weather_df = pd.DataFrame(weather_rows)
weather_df.to_csv(os.path.join(RAW_DIR, 'weather.csv'), index=False)
print(f"weather.csv: {len(weather_df)} rows")

# ── 3. passenger_traffic.csv ─────────────────────────────────────────────────
# Hourly passenger counts per terminal per day (6am–10pm)
hours = list(range(6, 23))

traffic_rows = []
for date in dates:
    is_weekend = date.weekday() >= 5
    base_multiplier = 1.3 if is_weekend else 1.0
    for terminal in terminals:
        for hour in hours:
            # Morning and evening peaks
            if 7 <= hour <= 9:
                peak = 1.8
            elif 16 <= hour <= 19:
                peak = 1.6
            else:
                peak = 1.0
            count = int(np.clip(
                np.random.normal(200 * base_multiplier * peak, 40), 50, 600
            ))
            traffic_rows.append({
                'date': date.strftime('%Y-%m-%d'),
                'terminal': terminal,
                'hour': hour,
                'passenger_count': count,
            })

traffic_df = pd.DataFrame(traffic_rows)
traffic_df.to_csv(os.path.join(RAW_DIR, 'passenger_traffic.csv'), index=False)
print(f"passenger_traffic.csv: {len(traffic_df)} rows")

# ── 4. security_wait_times.csv ───────────────────────────────────────────────
# Hourly observed wait times (minutes) per terminal – the prediction target
wait_rows = []
for _, row in traffic_df.iterrows():
    passengers = row['passenger_count']
    hour = row['hour']
    terminal = row['terminal']
    date_str = row['date']

    # Base wait scales with passenger count
    base_wait = passengers * 0.08

    # Longer waits during peak hours
    if 7 <= hour <= 9 or 16 <= hour <= 19:
        base_wait *= 1.4

    # Weather disruption lookup (use daily condition)
    day_weather = weather_df.loc[weather_df['date'] == date_str, 'condition'].values
    if len(day_weather) > 0 and day_weather[0] in ('Snow', 'Thunderstorm', 'Fog'):
        base_wait *= 1.3

    wait_minutes = round(float(np.clip(
        np.random.normal(base_wait, base_wait * 0.15), 5, 120
    )), 1)

    wait_rows.append({
        'date': date_str,
        'terminal': terminal,
        'hour': hour,
        'wait_time_minutes': wait_minutes,
    })

wait_df = pd.DataFrame(wait_rows)
wait_df.to_csv(os.path.join(RAW_DIR, 'security_wait_times.csv'), index=False)
print(f"security_wait_times.csv: {len(wait_df)} rows")

print("\nAll sample data files written to data/raw/")
