# Project Guide — Airport Security Wait Time Prediction

A step-by-step reference for understanding, running, and extending this project.

---

## Quick Start

Run the full pipeline from the project root in order:

```bash
python scripts/generate_sample_data.py   # 1. create raw CSV files
python scripts/import_data.py            # 2. load CSVs into SQLite
python scripts/clean_data.py             # 3. clean and validate data
python scripts/sql_queries.py            # 4. run analytical SQL queries
python scripts/model_training.py         # 5. train the prediction model
python scripts/prediction.py             # 6. generate predictions + chart
```

Open the notebook for interactive exploration:

```bash
jupyter notebook notebooks/exploration.ipynb
```

---

## What Each Script Does

### `generate_sample_data.py`
Generates four synthetic CSV files in `data/raw/`:

| File | Rows | Description |
|------|------|-------------|
| `flights.csv` | ~1,777 | Flight schedules, airlines, terminals, delays (90 days) |
| `weather.csv` | 90 | Daily weather condition, temperature, wind, visibility |
| `passenger_traffic.csv` | 9,180 | Hourly passenger counts per terminal |
| `security_wait_times.csv` | 9,180 | Hourly observed wait times — the prediction target |

### `import_data.py`
- Creates four tables in `database/airport_waits.db` with explicit schemas
- Loads all CSV rows using `pandas.to_sql`
- Prints a row-count summary to confirm the load

### `clean_data.py`
For each table, applies these cleaning steps:
- Parse dates; drop rows with invalid dates
- Clamp numeric columns to realistic ranges (e.g., delay 0–300 min)
- Fill missing numerics with column median
- Filter out rows with unrecognised terminals or airlines
- Writes cleaned data back as `cleaned_<table>` in the database and as CSVs in `data/cleaned/`

### `sql_queries.py`
Runs seven analytical queries demonstrating SQL skills:

1. Average wait time by terminal
2. Average wait time by hour of day
3. Top 10 busiest days by passenger count
4. Wait time vs weather condition (JOIN)
5. Airline delay statistics (aggregation + CASE WHEN)
6. Peak wait hour per terminal (window function RANK)
7. Daily average passengers vs wait time

### `model_training.py`
- Joins all cleaned tables into one feature matrix
- Engineers features: `is_peak_hour`, `is_weekend`, `weather_severity`, `terminal_code`, `day_of_week`
- Splits 80/20 train/test, fits a **Linear Regression** model
- Reports MAE, RMSE, and R² on the test set
- Saves the trained model to `database/model.pkl` using `pickle`

**Current model performance:**
- MAE ≈ 4 minutes
- R² ≈ 0.87

### `prediction.py`
- Loads `model.pkl`
- Generates predictions for every (terminal, hour) pair across two scenarios:
  - Weekday, clear weather
  - Weekend, rainy weather
- Saves a comparison chart to `visualizations/predicted_wait_times.png`
- Shows a single-point prediction example

---

## Database Schema

```sql
flights (flight_id, date, airline, terminal, scheduled_departure,
         delay_minutes, flight_status)

weather (date PK, condition, temperature_f, wind_speed_mph, visibility_miles)

passenger_traffic (id, date, terminal, hour, passenger_count)

security_wait_times (id, date, terminal, hour, wait_time_minutes)

-- Cleaned versions of each table are prefixed with cleaned_
cleaned_flights | cleaned_weather | cleaned_passenger_traffic | cleaned_security_wait_times
```

---

## Project Structure

```
Airport_analytics/
├── data/
│   ├── raw/                    # Original generated CSV files
│   └── cleaned/                # Cleaned CSV files
├── database/
│   ├── airport_waits.db        # SQLite database
│   └── model.pkl               # Trained model
├── notebooks/
│   └── exploration.ipynb       # EDA notebook (7 charts)
├── scripts/
│   ├── generate_sample_data.py
│   ├── import_data.py
│   ├── clean_data.py
│   ├── sql_queries.py
│   ├── model_training.py
│   └── prediction.py
├── visualizations/
│   └── predicted_wait_times.png
├── requirements.txt
├── README.md
└── PROJECT_GUIDE.md
```

---

## Key Design Decisions

**Why SQLite?**
Lightweight, zero-configuration, and ships with Python. Perfect for a
portfolio project that doesn't need a server.

**Why Linear Regression?**
Beginner-friendly, interpretable coefficients, and performs well (R² ≈ 0.87)
on this dataset. Easy to swap out for Random Forest or XGBoost later.

**Why synthetic data?**
Real airport security wait time data is rarely public. Synthetic data lets us
control the signal (e.g., peaks at 7–9am and 4–7pm) so the model has
something meaningful to learn.

---

## Possible Future Improvements

- Connect to a live flight API (e.g., AviationStack) for real data
- Add a Streamlit web app for interactive predictions
- Replace Linear Regression with a Random Forest or Gradient Boosting model
- Integrate with Power BI or Tableau for dashboards
- Schedule daily data updates with a cron job
- Host the SQLite database on a cloud service
