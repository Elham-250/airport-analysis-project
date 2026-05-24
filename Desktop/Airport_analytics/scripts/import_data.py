"""
Loads the raw CSV files from data/raw/ into the SQLite database.
Run this script first in the pipeline.
"""

import os
import sqlite3
import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR   = os.path.join(BASE_DIR, 'data', 'raw')
DB_PATH   = os.path.join(BASE_DIR, 'database', 'airport_waits.db')

CSV_TABLES = {
    'flights':              'flights.csv',
    'weather':              'weather.csv',
    'passenger_traffic':    'passenger_traffic.csv',
    'security_wait_times':  'security_wait_times.csv',
}

def create_tables(conn):
    """Create tables with explicit schemas before loading data."""
    cursor = conn.cursor()

    cursor.executescript("""
        DROP TABLE IF EXISTS flights;
        CREATE TABLE flights (
            flight_id        INTEGER PRIMARY KEY,
            date             TEXT NOT NULL,
            airline          TEXT NOT NULL,
            terminal         TEXT NOT NULL,
            scheduled_departure TEXT NOT NULL,
            delay_minutes    INTEGER NOT NULL,
            flight_status    TEXT NOT NULL
        );

        DROP TABLE IF EXISTS weather;
        CREATE TABLE weather (
            date             TEXT PRIMARY KEY,
            condition        TEXT NOT NULL,
            temperature_f    REAL NOT NULL,
            wind_speed_mph   REAL NOT NULL,
            visibility_miles REAL NOT NULL
        );

        DROP TABLE IF EXISTS passenger_traffic;
        CREATE TABLE passenger_traffic (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            date             TEXT NOT NULL,
            terminal         TEXT NOT NULL,
            hour             INTEGER NOT NULL,
            passenger_count  INTEGER NOT NULL
        );

        DROP TABLE IF EXISTS security_wait_times;
        CREATE TABLE security_wait_times (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            date             TEXT NOT NULL,
            terminal         TEXT NOT NULL,
            hour             INTEGER NOT NULL,
            wait_time_minutes REAL NOT NULL
        );
    """)
    conn.commit()
    print("Tables created.")


def load_csv_to_table(conn, table_name, csv_filename):
    """Read a CSV and insert all rows into the given table."""
    csv_path = os.path.join(RAW_DIR, csv_filename)
    df = pd.read_csv(csv_path)

    # Remove auto-increment primary key column if present so SQLite assigns it
    if table_name in ('passenger_traffic', 'security_wait_times') and 'id' in df.columns:
        df = df.drop(columns=['id'])

    df.to_sql(table_name, conn, if_exists='append', index=False)
    print(f"  Loaded {len(df):,} rows into '{table_name}'")


def verify_counts(conn):
    """Print row counts for each table."""
    cursor = conn.cursor()
    print("\nRow counts in database:")
    for table in CSV_TABLES:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table}: {count:,}")


def main():
    print(f"Database: {DB_PATH}\n")
    conn = sqlite3.connect(DB_PATH)

    create_tables(conn)
    print("\nLoading CSV files:")
    for table_name, csv_file in CSV_TABLES.items():
        load_csv_to_table(conn, table_name, csv_file)

    verify_counts(conn)
    conn.close()
    print("\nimport_data.py complete.")


if __name__ == '__main__':
    main()
