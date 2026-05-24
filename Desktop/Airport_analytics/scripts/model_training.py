"""
Builds a feature matrix from the cleaned database tables, trains a
Linear Regression model to predict security wait times, evaluates it,
and saves the trained model to database/model.pkl.

Run after clean_data.py.
"""

import os
import pickle
import sqlite3

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH    = os.path.join(BASE_DIR, 'database', 'airport_waits.db')
MODEL_PATH = os.path.join(BASE_DIR, 'database', 'model.pkl')

WEATHER_SEVERITY = {
    'Clear': 0, 'Cloudy': 1, 'Rain': 2, 'Fog': 3, 'Snow': 4, 'Thunderstorm': 5
}


def load_data(conn):
    """Join cleaned tables into a single feature-rich DataFrame."""
    sql = """
        SELECT
            s.date,
            s.terminal,
            s.hour,
            s.wait_time_minutes,
            p.passenger_count,
            w.condition      AS weather_condition,
            w.temperature_f,
            w.wind_speed_mph,
            w.visibility_miles
        FROM cleaned_security_wait_times  s
        JOIN cleaned_passenger_traffic    p
          ON s.date = p.date AND s.terminal = p.terminal AND s.hour = p.hour
        JOIN cleaned_weather              w
          ON s.date = w.date
    """
    df = pd.read_sql_query(sql, conn)
    return df


def engineer_features(df):
    """Add derived features useful for prediction."""
    df = df.copy()

    # Day of week (0=Monday … 6=Sunday)
    df['day_of_week'] = pd.to_datetime(df['date']).dt.dayofweek

    # Binary: is it a weekend?
    df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)

    # Binary: is it a morning or evening peak hour?
    df['is_peak_hour'] = df['hour'].apply(
        lambda h: 1 if (7 <= h <= 9) or (16 <= h <= 19) else 0
    )

    # Encode terminal as integer (A=0, B=1, …)
    terminal_enc = LabelEncoder()
    df['terminal_code'] = terminal_enc.fit_transform(df['terminal'])

    # Map weather to a severity score
    df['weather_severity'] = df['weather_condition'].map(WEATHER_SEVERITY).fillna(0)

    return df, terminal_enc


FEATURE_COLS = [
    'hour',
    'passenger_count',
    'is_weekend',
    'is_peak_hour',
    'terminal_code',
    'weather_severity',
    'temperature_f',
    'wind_speed_mph',
    'visibility_miles',
    'day_of_week',
]
TARGET_COL = 'wait_time_minutes'


def train_model(df):
    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mae  = mean_absolute_error(y_test, y_pred)
    rmse = root_mean_squared_error(y_test, y_pred)
    r2   = r2_score(y_test, y_pred)

    print(f"  Training samples : {len(X_train):,}")
    print(f"  Test samples     : {len(X_test):,}")
    print(f"  MAE              : {mae:.2f} minutes")
    print(f"  RMSE             : {rmse:.2f} minutes")
    print(f"  R2 score         : {r2:.4f}")

    # Feature importance (coefficient magnitude)
    coeff_df = pd.DataFrame({
        'feature':     FEATURE_COLS,
        'coefficient': model.coef_,
    }).sort_values('coefficient', key=abs, ascending=False)

    print("\n  Feature coefficients:")
    print(coeff_df.to_string(index=False))

    return model


def save_model(model, terminal_enc):
    payload = {
        'model':        model,
        'terminal_enc': terminal_enc,
        'feature_cols': FEATURE_COLS,
    }
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(payload, f)
    print(f"\nModel saved to: {MODEL_PATH}")


def main():
    conn = sqlite3.connect(DB_PATH)
    print("Loading and joining tables...")
    df = load_data(conn)
    conn.close()

    print(f"Dataset shape: {df.shape}")
    df, terminal_enc = engineer_features(df)

    print("\nTraining Linear Regression model...")
    model = train_model(df)

    save_model(model, terminal_enc)
    print("\nmodel_training.py complete.")


if __name__ == '__main__':
    main()
