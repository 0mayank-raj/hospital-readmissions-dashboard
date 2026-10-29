from pathlib import Path
import pandas as pd

# Locate the project directory
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Define the dataset path
DATA_PATH = PROJECT_DIR / "data" / "raw" / "diabetic_data.csv"

# Check whether the file exists
if not DATA_PATH.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

# Load the dataset
df = pd.read_csv(DATA_PATH)

# Display basic information
print("\n========== DATASET OVERVIEW ==========")
print(f"Number of rows: {df.shape[0]}")
print(f"Number of columns: {df.shape[1]}")

print("\n========== FIRST FIVE ROWS ==========")
print(df.head())

print("\n========== COLUMN NAMES ==========")
print(df.columns.tolist())

print("\n========== DATA TYPES ==========")
print(df.dtypes)

print("\n========== MISSING VALUE COUNTS ==========")
print(df.isin(["?"]).sum().sort_values(ascending=False).head(15))

print("\n========== READMISSION DISTRIBUTION ==========")
print(df["readmitted"].value_counts(dropna=False))

print("\n========== UNIQUE PATIENTS ==========")
print(df["patient_nbr"].nunique())

print("\n========== DUPLICATE ENCOUNTER IDS ==========")
print(df["encounter_id"].duplicated().sum())
