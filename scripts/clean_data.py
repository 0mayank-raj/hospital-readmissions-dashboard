from pathlib import Path
import json

import pandas as pd


# --------------------------------------------------
# 1. DEFINE PROJECT PATHS
# --------------------------------------------------

PROJECT_DIR = Path(__file__).resolve().parent.parent

RAW_PATH = PROJECT_DIR / "data" / "raw" / "diabetic_data.csv"
PROCESSED_DIR = PROJECT_DIR / "data" / "processed"
REPORTS_DIR = PROJECT_DIR / "reports"

CLEAN_PATH = PROCESSED_DIR / "diabetic_data_cleaned.csv"
REPORT_PATH = REPORTS_DIR / "validation_report.json"


# --------------------------------------------------
# 2. CREATE OUTPUT DIRECTORIES
# --------------------------------------------------

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 3. LOAD RAW DATA
# --------------------------------------------------

if not RAW_PATH.exists():
    raise FileNotFoundError(f"Dataset not found: {RAW_PATH}")

df = pd.read_csv(RAW_PATH)

raw_row_count = len(df)

print(f"Original rows: {raw_row_count}")


# --------------------------------------------------
# 4. CHECK REQUIRED COLUMNS
# --------------------------------------------------

required_columns = [
    "encounter_id",
    "patient_nbr",
    "discharge_disposition_id",
    "time_in_hospital",
    "readmitted",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Required columns missing: {missing_columns}"
    )


# --------------------------------------------------
# 5. REPLACE QUESTION MARKS WITH NULL VALUES
# --------------------------------------------------

df = df.replace("?", pd.NA)

print("\nMissing values after replacing '?':")

print(
    df.isna()
    .sum()
    .sort_values(ascending=False)
    .head(10)
)


# --------------------------------------------------
# 6. DROP THE MOSTLY MISSING WEIGHT COLUMN
# --------------------------------------------------

if "weight" in df.columns:
    df = df.drop(columns=["weight"])


# --------------------------------------------------
# 7. VALIDATE ENCOUNTER IDENTIFIERS
# --------------------------------------------------

duplicate_encounters = int(
    df["encounter_id"].duplicated().sum()
)

if duplicate_encounters > 0:
    raise ValueError(
        f"Found {duplicate_encounters} duplicate encounter IDs"
    )


# --------------------------------------------------
# 8. EXCLUDE DEATH AND HOSPICE DISPOSITIONS
# --------------------------------------------------

excluded_dispositions = [11, 13, 14, 19, 20, 21]

excluded_mask = df["discharge_disposition_id"].isin(
    excluded_dispositions
)

excluded_count = int(excluded_mask.sum())

df = df.loc[~excluded_mask].copy()

print(f"\nExcluded encounters: {excluded_count}")
print(f"Rows after exclusions: {len(df)}")


# --------------------------------------------------
# 9. CREATE THE 30-DAY READMISSION FLAG
# --------------------------------------------------

df["readmitted_30d"] = (
    df["readmitted"] == "<30"
).astype("int8")


# --------------------------------------------------
# 10. VALIDATE READMISSION VALUES
# --------------------------------------------------

allowed_readmission_values = {"NO", ">30", "<30"}

unexpected_readmission_values = (
    set(df["readmitted"].dropna().unique())
    - allowed_readmission_values
)

if unexpected_readmission_values:
    raise ValueError(
        "Unexpected readmission values: "
        f"{unexpected_readmission_values}"
    )

if not df["readmitted_30d"].isin([0, 1]).all():
    raise ValueError("Readmission flag must contain only 0 and 1")


# --------------------------------------------------
# 11. VALIDATE LENGTH OF STAY
# --------------------------------------------------

los_min = int(df["time_in_hospital"].min())
los_max = int(df["time_in_hospital"].max())

invalid_los_count = int(
    (
        (df["time_in_hospital"] < 1)
        | (df["time_in_hospital"] > 14)
    ).sum()
)

if invalid_los_count > 0:
    raise ValueError(
        f"Found {invalid_los_count} invalid length-of-stay values"
    )


# --------------------------------------------------
# 12. CHECK MISSING VALUES
# --------------------------------------------------

null_counts = (
    df.isna()
    .sum()
    .sort_values(ascending=False)
)

null_percentages = (
    (df.isna().mean() * 100)
    .round(2)
    .sort_values(ascending=False)
)


# --------------------------------------------------
# 13. CHECK PATIENT AND ENCOUNTER COUNTS
# --------------------------------------------------

unique_patients = int(df["patient_nbr"].nunique())

unique_encounters = int(df["encounter_id"].nunique())

duplicate_encounters_after = int(
    df["encounter_id"].duplicated().sum()
)


# --------------------------------------------------
# 14. SAVE CLEANED DATA
# --------------------------------------------------

df.to_csv(CLEAN_PATH, index=False)


# --------------------------------------------------
# 15. GENERATE VALIDATION REPORT
# --------------------------------------------------

report = {
    "raw_row_count": raw_row_count,
    "cleaned_row_count": len(df),
    "rows_excluded": excluded_count,
    "columns_after_cleaning": len(df.columns),
    "unique_patients": unique_patients,
    "unique_encounters": unique_encounters,
    "duplicate_encounters_before_cleaning": (
        duplicate_encounters
    ),
    "duplicate_encounters_after_cleaning": (
        duplicate_encounters_after
    ),
    "weight_column_dropped": True,
    "excluded_discharge_dispositions": (
        excluded_dispositions
    ),
    "length_of_stay_min": los_min,
    "length_of_stay_max": los_max,
    "invalid_length_of_stay_count": invalid_los_count,
    "readmission_flag_values": sorted(
        df["readmitted_30d"].unique().tolist()
    ),
    "readmission_distribution": {
        str(key): int(value)
        for key, value in df["readmitted"].value_counts(
            dropna=False
        ).items()
    },
    "missing_value_counts": {
        str(key): int(value)
        for key, value in null_counts.items()
    },
    "missing_value_percentages": {
        str(key): float(value)
        for key, value in null_percentages.items()
    },
}

with open(REPORT_PATH, "w", encoding="utf-8") as file:
    json.dump(report, file, indent=4)


# --------------------------------------------------
# 16. DISPLAY SUMMARY
# --------------------------------------------------

print("\n========== CLEANING SUMMARY ==========")

print(f"Original rows: {raw_row_count}")
print(f"Excluded rows: {excluded_count}")
print(f"Cleaned rows: {len(df)}")
print(f"Columns after cleaning: {len(df.columns)}")
print(f"Unique patients: {unique_patients}")
print(f"Unique encounters: {unique_encounters}")
print(f"Duplicate encounters remaining: {duplicate_encounters_after}")

print("\nReadmission flag distribution:")

print(df["readmitted_30d"].value_counts())

print("\nLength of stay:")

print(f"Minimum: {los_min}")
print(f"Maximum: {los_max}")

print("\nCleaned dataset saved to:")
print(CLEAN_PATH)

print("\nValidation report saved to:")
print(REPORT_PATH)
