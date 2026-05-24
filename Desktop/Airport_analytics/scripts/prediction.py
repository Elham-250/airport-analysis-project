"""
Uses the trained model to predict security wait times for a given scenario
and generates a visualization of predicted wait times across all hours
and terminals for a specified day.

Run after model_training.py.
"""

import os
import pickle

import matplotlib
matplotlib.use('Agg')  # non-interactive backend for saving to file
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'database', 'model.pkl')
VIZ_DIR    = os.path.join(BASE_DIR, 'visualizations')
os.makedirs(VIZ_DIR, exist_ok=True)

WEATHER_SEVERITY = {
    'Clear': 0, 'Cloudy': 1, 'Rain': 2, 'Fog': 3, 'Snow': 4, 'Thunderstorm': 5
}
TERMINALS = ['A', 'B', 'C', 'D', 'E', 'F']
HOURS     = list(range(6, 23))


def load_model():
    with open(MODEL_PATH, 'rb') as f:
        return pickle.load(f)


def predict_single(payload, model_data):
    """
    Predict wait time for one scenario.
    payload keys: terminal, hour, passenger_count, weather_condition,
                  temperature_f, wind_speed_mph, visibility_miles,
                  is_weekend, day_of_week
    """
    model        = model_data['model']
    terminal_enc = model_data['terminal_enc']
    feature_cols = model_data['feature_cols']

    terminal_code    = terminal_enc.transform([payload['terminal']])[0]
    weather_severity = WEATHER_SEVERITY.get(payload['weather_condition'], 0)
    is_peak_hour     = 1 if (7 <= payload['hour'] <= 9) or (16 <= payload['hour'] <= 19) else 0

    row = pd.DataFrame([{
        'hour':             payload['hour'],
        'passenger_count':  payload['passenger_count'],
        'is_weekend':       payload['is_weekend'],
        'is_peak_hour':     is_peak_hour,
        'terminal_code':    terminal_code,
        'weather_severity': weather_severity,
        'temperature_f':    payload['temperature_f'],
        'wind_speed_mph':   payload['wind_speed_mph'],
        'visibility_miles': payload['visibility_miles'],
        'day_of_week':      payload['day_of_week'],
    }])

    prediction = model.predict(row[feature_cols])[0]
    return round(max(prediction, 0), 1)


def predict_day(model_data, weather_condition, is_weekend, day_of_week,
                temperature_f=65.0, wind_speed_mph=8.0, visibility_miles=9.0,
                base_passengers=250):
    """
    Generate predictions for every (terminal, hour) combination for one day.
    Returns a DataFrame with columns: terminal, hour, predicted_wait_minutes
    """
    rows = []
    for terminal in TERMINALS:
        for hour in HOURS:
            if (7 <= hour <= 9) or (16 <= hour <= 19):
                passengers = int(base_passengers * 1.7)
            else:
                passengers = base_passengers
            if is_weekend:
                passengers = int(passengers * 1.3)

            wait = predict_single({
                'terminal':         terminal,
                'hour':             hour,
                'passenger_count':  passengers,
                'weather_condition': weather_condition,
                'temperature_f':    temperature_f,
                'wind_speed_mph':   wind_speed_mph,
                'visibility_miles': visibility_miles,
                'is_weekend':       int(is_weekend),
                'day_of_week':      day_of_week,
            }, model_data)
            rows.append({'terminal': terminal, 'hour': hour, 'predicted_wait_minutes': wait})

    return pd.DataFrame(rows)


def print_scenario(label, df):
    print(f"\n{label}")
    pivot = df.pivot(index='hour', columns='terminal', values='predicted_wait_minutes')
    print(pivot.to_string())


def plot_predictions(df_weekday, df_weekend_rain, output_path):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)

    for ax, (df, title) in zip(axes, [
        (df_weekday,     'Weekday - Clear Weather'),
        (df_weekend_rain, 'Weekend - Rainy Weather'),
    ]):
        for terminal in TERMINALS:
            subset = df[df['terminal'] == terminal]
            ax.plot(subset['hour'], subset['predicted_wait_minutes'],
                    marker='o', markersize=4, label=f'Terminal {terminal}')

        ax.set_title(title)
        ax.set_xlabel('Hour of Day')
        ax.set_ylabel('Predicted Wait Time (minutes)')
        ax.set_xticks(HOURS)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.suptitle('Airport Security Predicted Wait Times by Terminal', fontsize=13)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"\nPlot saved to: {output_path}")


def main():
    model_data = load_model()

    # ── Scenario 1: clear weekday ─────────────────────────────────────────────
    df_weekday = predict_day(
        model_data,
        weather_condition='Clear',
        is_weekend=False,
        day_of_week=1,          # Tuesday
        temperature_f=68.0,
        wind_speed_mph=7.0,
        visibility_miles=10.0,
        base_passengers=250,
    )
    print_scenario("=== Scenario 1: Weekday (Tuesday), Clear Weather ===", df_weekday)

    # ── Scenario 2: rainy weekend ─────────────────────────────────────────────
    df_weekend_rain = predict_day(
        model_data,
        weather_condition='Rain',
        is_weekend=True,
        day_of_week=6,          # Sunday
        temperature_f=55.0,
        wind_speed_mph=15.0,
        visibility_miles=5.0,
        base_passengers=250,
    )
    print_scenario("=== Scenario 2: Weekend (Sunday), Rainy Weather ===", df_weekend_rain)

    # ── Single-point prediction example ──────────────────────────────────────
    single_wait = predict_single({
        'terminal':         'C',
        'hour':             8,
        'passenger_count':  420,
        'weather_condition': 'Snow',
        'temperature_f':    30.0,
        'wind_speed_mph':   20.0,
        'visibility_miles': 2.0,
        'is_weekend':       0,
        'day_of_week':      2,
    }, model_data)
    print(f"\nSingle prediction: Terminal C, 8am, Snow, 420 passengers")
    print(f"  Predicted wait time: {single_wait} minutes")

    # ── Plot ──────────────────────────────────────────────────────────────────
    out_path = os.path.join(VIZ_DIR, 'predicted_wait_times.png')
    plot_predictions(df_weekday, df_weekend_rain, out_path)

    print("\nprediction.py complete.")


if __name__ == '__main__':
    main()
