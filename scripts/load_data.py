from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# 1. Locate the project directory
PROJECT_DIR = Path(__file__).resolve().parent.parent

# 2. Load database configuration
load_dotenv(PROJECT_DIR / ".env")

required_settings = [
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
]

missing_settings = [
    key for key in required_settings
    if not os.getenv(key)
]

if missing_settings:
    raise ValueError(
        f"Missing database settings in .env: {missing_settings}"
    )


# 3. Define the cleaned dataset path
CSV_PATH = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "diabetic_data_cleaned.csv"
)

if not CSV_PATH.exists():
    raise FileNotFoundError(
        f"Cleaned dataset not found: {CSV_PATH}"
    )


# 4. Create the PostgreSQL connection
connection_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"],
)

engine = create_engine(
    connection_url,
    pool_pre_ping=True,
)


# 5. Load and validate the CSV
print("Reading cleaned dataset...")

df = pd.read_csv(CSV_PATH)

if df["encounter_id"].isna().any():
    raise ValueError("Encounter IDs cannot be missing.")

if df["encounter_id"].duplicated().any():
    raise ValueError("Duplicate encounter IDs detected.")

expected_rows = len(df)

print(f"Rows to load: {expected_rows}")
print(f"Columns to load: {len(df.columns)}")


# 6. Load data into PostgreSQL
# This replaces only the encounters table.
# Other database tables are not dropped.

print("\nLoading data into PostgreSQL...")

with engine.begin() as connection:
    connection.execute(
        text("""
            CREATE TABLE IF NOT EXISTS encounters (
                encounter_id BIGINT PRIMARY KEY
            )
        """)
    )

    connection.execute(
        text("""
            DROP TABLE IF EXISTS encounters
        """)
    )

    df.to_sql(
        name="encounters",
        con=connection,
        if_exists="replace",
        index=False,
        chunksize=500,
        method="multi",
    )


# 7. Verify the loaded row count
with engine.connect() as connection:
    actual_rows = connection.execute(
        text("SELECT COUNT(*) FROM encounters")
    ).scalar_one()

    unique_encounters = connection.execute(
        text("""
            SELECT COUNT(DISTINCT encounter_id)
            FROM encounters
        """)
    ).scalar_one()

    database_name = connection.execute(
        text("SELECT current_database()")
    ).scalar_one()


# 8. Report the results
print("\n========== DATABASE LOAD SUMMARY ==========")
print(f"Database: {database_name}")
print(f"Expected rows: {expected_rows}")
print(f"Loaded rows: {actual_rows}")
print(f"Unique encounter IDs: {unique_encounters}")

if actual_rows != expected_rows:
    raise RuntimeError("Loaded row count does not match CSV row count.")

if unique_encounters != actual_rows:
    raise RuntimeError("Encounter IDs are not unique.")

print("\nData loaded and validated successfully!")

engine.dispose()
