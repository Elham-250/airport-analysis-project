"""
Reads raw tables from the database, applies cleaning rules,
and writes the cleaned results to data/cleaned/ as CSVs and
back into the database as cleaned_* tables.

Run after import_data.py.
"""

import os
import sqlite3
import pandas as pd

BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH     = os.path.join(BASE_DIR, 'database', 'airport_waits.db')
CLEANED_DIR = os.path.join(BASE_DIR, 'data', 'cleaned')
os.makedirs(CLEANED_DIR, exist_ok=True)

VALID_TERMINALS = {'A', 'B', 'C', 'D', 'E', 'F'}
VALID_AIRLINES  = {'Delta', 'United', 'Southwest', 'American'}


def load_table(conn, table_name):
    return pd.read_sql_query(f"SELECT * FROM {table_name}", conn)


def clean_flights(df):
    before = len(df)
    df = df.copy()

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])

    df['delay_minutes'] = pd.to_numeric(df['delay_minutes'], errors='coerce').fillna(0).astype(int)
    df['delay_minutes'] = df['delay_minutes'].clip(lower=0, upper=300)

    df = df[df['terminal'].isin(VALID_TERMINALS)]
    df = df[df['airline'].isin(VALID_AIRLINES)]

    # Recalculate status from cleaned delay value
    df['flight_status'] = df['delay_minutes'].apply(
        lambda d: 'Delayed' if d > 15 else 'On Time'
    )

    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    print(f"  flights:            {before:,} -> {len(df):,} rows (removed {before - len(df)})")
    return df


def clean_weather(df):
    before = len(df)
    df = df.copy()

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])
    df = df.drop_duplicates(subset=['date'])

    df['temperature_f']    = pd.to_numeric(df['temperature_f'],    errors='coerce')
    df['wind_speed_mph']   = pd.to_numeric(df['wind_speed_mph'],   errors='coerce')
    df['visibility_miles'] = pd.to_numeric(df['visibility_miles'], errors='coerce')

    # Fill missing numeric columns with median
    for col in ['temperature_f', 'wind_speed_mph', 'visibility_miles']:
        df[col] = df[col].fillna(df[col].median())

    df['temperature_f']    = df['temperature_f'].clip(-60, 130)
    df['wind_speed_mph']   = df['wind_speed_mph'].clip(0, 150)
    df['visibility_miles'] = df['visibility_miles'].clip(0, 10)

    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    print(f"  weather:            {before:,} -> {len(df):,} rows (removed {before - len(df)})")
    return df


def clean_passenger_traffic(df):
    before = len(df)
    df = df.copy()

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])

    df = df[df['terminal'].isin(VALID_TERMINALS)]
    df['hour'] = pd.to_numeric(df['hour'], errors='coerce')
    df = df[df['hour'].between(0, 23)]

    df['passenger_count'] = pd.to_numeric(df['passenger_count'], errors='coerce')
    df['passenger_count'] = df['passenger_count'].fillna(0).clip(lower=0).astype(int)

    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    print(f"  passenger_traffic:  {before:,} -> {len(df):,} rows (removed {before - len(df)})")
    return df


def clean_wait_times(df):
    before = len(df)
    df = df.copy()

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date'])

    df = df[df['terminal'].isin(VALID_TERMINALS)]
    df['hour'] = pd.to_numeric(df['hour'], errors='coerce')
    df = df[df['hour'].between(0, 23)]

    df['wait_time_minutes'] = pd.to_numeric(df['wait_time_minutes'], errors='coerce')
    df = df.dropna(subset=['wait_time_minutes'])
    df['wait_time_minutes'] = df['wait_time_minutes'].clip(lower=0, upper=180)

    df['date'] = df['date'].dt.strftime('%Y-%m-%d')
    print(f"  security_wait_times:{before:,} -> {len(df):,} rows (removed {before - len(df)})")
    return df


def save_cleaned(conn, df, table_name):
    """Write cleaned data to CSV and to database as cleaned_<table>."""
    csv_path = os.path.join(CLEANED_DIR, f"{table_name}.csv")
    df.to_csv(csv_path, index=False)

    db_table = f"cleaned_{table_name}"
    df.to_sql(db_table, conn, if_exists='replace', index=False)


def main():
    conn = sqlite3.connect(DB_PATH)
    print("Cleaning tables:\n")

    tables = {
        'flights':             clean_flights,
        'weather':             clean_weather,
        'passenger_traffic':   clean_passenger_traffic,
        'security_wait_times': clean_wait_times,
    }

    for table_name, clean_fn in tables.items():
        df_raw     = load_table(conn, table_name)
        df_cleaned = clean_fn(df_raw)
        save_cleaned(conn, df_cleaned, table_name)

    conn.close()
    print(f"\nCleaned CSVs written to: {CLEANED_DIR}")
    print("Cleaned tables saved in database as cleaned_<table>.")
    print("\nclean_data.py complete.")


if __name__ == '__main__':
    main()
