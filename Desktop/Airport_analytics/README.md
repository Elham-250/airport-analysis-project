# Airport Security Wait Time Prediction System

A portfolio project that predicts airport security wait times using Python and SQL.

## What It Does

- Stores historical flight, weather, and passenger data in a SQLite database
- Cleans and prepares raw data for analysis
- Runs SQL queries to identify patterns and trends
- Trains a simple machine learning model (Linear Regression) to predict wait times
- Generates visualizations of wait time trends

## Project Structure

```
Airport_analytics/
├── data/
│   ├── raw/          # Original CSV data files
│   └── cleaned/      # Cleaned data ready for analysis
├── database/
│   └── airport_waits.db   # SQLite database
├── notebooks/
│   └── exploration.ipynb  # Exploratory data analysis
├── scripts/
│   ├── import_data.py     # Load CSV data into database
│   ├── clean_data.py      # Clean and preprocess data
│   ├── sql_queries.py     # Analytical SQL queries
│   ├── model_training.py  # Train the prediction model
│   └── prediction.py      # Generate wait time predictions
├── visualizations/        # Output charts and graphs
├── requirements.txt
└── PROJECT_GUIDE.md
```

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the pipeline in order:
   ```
   python scripts/import_data.py
   python scripts/clean_data.py
   python scripts/sql_queries.py
   python scripts/model_training.py
   python scripts/prediction.py
   ```

3. Open the notebook for exploration:
   ```
   jupyter notebook notebooks/exploration.ipynb
   ```

## Tech Stack

- **Language:** Python, SQL
- **Database:** SQLite
- **Libraries:** pandas, numpy, matplotlib, scikit-learn
