# Airport Security Wait Time Prediction System

This file provides guidance to Claude Code when working in this repository.

---

# Project Overview

The goal of this project is to build a small-scale airport security wait-time prediction and analytics system using Python and SQL.

The system analyzes historical airport-related data such as:
- flight schedules
- delays
- weather conditions
- passenger traffic patterns
- time and date information

The project predicts estimated airport security wait times based on operational conditions instead of generic airport recommendations.

This is a student portfolio project focused on:
- data analytics
- SQL usage
- predictive modeling
- operational problem solving
- software/data engineering fundamentals

The project is intentionally lightweight and designed to be expandable in the future.

---

# Project Rules

- Keep the project simple and achievable within a short timeframe.
- Focus on functionality and clean structure rather than perfection.
- Use realistic datasets when possible.
- Avoid overengineering.
- Prioritize learning and demonstration of skills.
- The project must clearly demonstrate:
  - SQL usage
  - Python data analysis
  - data cleaning
  - querying structured data
  - basic predictive analytics

- Build a minimum viable product (MVP) first before adding advanced features.
- All code should remain beginner-friendly and understandable.
- Comments and explanations should be clear.

---

# Tech Stack

## Languages
- Python
- SQL

## Database
- SQLite

## Python Libraries
- pandas
- sqlite3
- matplotlib
- numpy
- scikit-learn

## Development Tools
- VS Code
- Git/GitHub

---

# Project Structure

```text
project_root/
│
├── data/
│   ├── raw/
│   ├── cleaned/
│
├── database/
│   ├── airport_waits.db
│
├── notebooks/
│   ├── exploration.ipynb
│
├── scripts/
│   ├── import_data.py
│   ├── clean_data.py
│   ├── sql_queries.py
│   ├── model_training.py
│   ├── prediction.py
│
├── visualizations/
│
├── README.md
├── requirements.txt
└── PROJECT_GUIDE.md

#Code Conventions
Use descriptive variable names.
Keep functions small and focused.
Add comments for complex logic.
Use snake_case for Python variables and functions.
Separate SQL queries logically.
Keep files modular and organized.
Avoid hardcoding values whenever possible.
Write readable SQL queries with proper formatting.

## What to Avoid
Avoid building a full production-level application.
Avoid unnecessary frameworks.
Avoid premature optimization.
Avoid making the database overly complex.
Avoid advanced machine learning initially.
Avoid spending too much time on UI/design.
Avoid collecting excessive datasets.
Avoid trying to solve every airport problem.

This project is meant to demonstrate:

analytical thinking
SQL integration
data workflows
beginner predictive analytics

##Notes
Primary Goal

Demonstrate practical usage of:

SQL
Python
data analysis
prediction systems
Future Improvements

Possible future upgrades:

live airport APIs
real-time flight data
dashboards
Power BI integration
Streamlit web app
cloud database hosting
more advanced machine learning models
MVP Definition

A successful MVP should:

store data in SQL
query data using SQL
analyze data with Python
generate simple wait-time predictions
visualize trends using graphs