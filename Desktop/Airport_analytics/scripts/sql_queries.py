"""
Runs a set of analytical SQL queries against the cleaned database tables
and prints the results. Demonstrates SQL usage for the portfolio project.

Run after clean_data.py.
"""

import os
import sqlite3
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH  = os.path.join(BASE_DIR, 'database', 'airport_waits.db')


def run_query(conn, title, sql):
    """Execute a SQL query, print its title and results."""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print('=' * 60)
    df = pd.read_sql_query(sql, conn)
    print(df.to_string(index=False))
    return df


def main():
    conn = sqlite3.connect(DB_PATH)

    # ── 1. Average wait time by terminal ─────────────────────────────────────
    run_query(conn, "1. Average Wait Time by Terminal", """
        SELECT
            terminal,
            ROUND(AVG(wait_time_minutes), 2) AS avg_wait_minutes,
            ROUND(MIN(wait_time_minutes), 2) AS min_wait_minutes,
            ROUND(MAX(wait_time_minutes), 2) AS max_wait_minutes
        FROM cleaned_security_wait_times
        GROUP BY terminal
        ORDER BY avg_wait_minutes DESC
    """)

    # ── 2. Average wait time by hour of day ──────────────────────────────────
    run_query(conn, "2. Average Wait Time by Hour of Day", """
        SELECT
            hour,
            ROUND(AVG(wait_time_minutes), 2) AS avg_wait_minutes,
            COUNT(*) AS observations
        FROM cleaned_security_wait_times
        GROUP BY hour
        ORDER BY hour
    """)

    # ── 3. Busiest days by total passenger count ──────────────────────────────
    run_query(conn, "3. Top 10 Busiest Days by Passenger Count", """
        SELECT
            date,
            SUM(passenger_count) AS total_passengers
        FROM cleaned_passenger_traffic
        GROUP BY date
        ORDER BY total_passengers DESC
        LIMIT 10
    """)

    # ── 4. Wait time vs weather condition ────────────────────────────────────
    run_query(conn, "4. Average Wait Time by Weather Condition", """
        SELECT
            w.condition,
            ROUND(AVG(s.wait_time_minutes), 2) AS avg_wait_minutes,
            COUNT(*) AS observations
        FROM cleaned_security_wait_times s
        JOIN cleaned_weather w ON s.date = w.date
        GROUP BY w.condition
        ORDER BY avg_wait_minutes DESC
    """)

    # ── 5. Airline delay statistics ───────────────────────────────────────────
    run_query(conn, "5. Delay Statistics by Airline", """
        SELECT
            airline,
            COUNT(*)                                          AS total_flights,
            SUM(CASE WHEN flight_status = 'Delayed' THEN 1 ELSE 0 END)
                                                              AS delayed_flights,
            ROUND(
                100.0 * SUM(CASE WHEN flight_status = 'Delayed' THEN 1 ELSE 0 END)
                / COUNT(*), 1
            )                                                 AS delay_pct,
            ROUND(AVG(delay_minutes), 1)                      AS avg_delay_minutes
        FROM cleaned_flights
        GROUP BY airline
        ORDER BY delay_pct DESC
    """)

    # ── 6. Peak wait hours per terminal ──────────────────────────────────────
    run_query(conn, "6. Peak Wait Hour per Terminal", """
        SELECT
            terminal,
            hour               AS peak_hour,
            ROUND(avg_wait, 2) AS avg_wait_minutes
        FROM (
            SELECT
                terminal,
                hour,
                AVG(wait_time_minutes) AS avg_wait,
                RANK() OVER (
                    PARTITION BY terminal
                    ORDER BY AVG(wait_time_minutes) DESC
                ) AS rnk
            FROM cleaned_security_wait_times
            GROUP BY terminal, hour
        )
        WHERE rnk = 1
        ORDER BY terminal
    """)

    # ── 7. Correlation proxy: passengers vs wait time (daily averages) ────────
    run_query(conn, "7. Daily Avg Passengers vs Avg Wait Time (first 10 days)", """
        SELECT
            p.date,
            ROUND(AVG(p.passenger_count), 0) AS avg_passengers,
            ROUND(AVG(s.wait_time_minutes),  2) AS avg_wait_minutes
        FROM cleaned_passenger_traffic  p
        JOIN cleaned_security_wait_times s
          ON p.date = s.date AND p.terminal = s.terminal AND p.hour = s.hour
        GROUP BY p.date
        ORDER BY p.date
        LIMIT 10
    """)

    conn.close()
    print("\nsql_queries.py complete.")


if __name__ == '__main__':
    main()
