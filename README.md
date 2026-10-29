# Hospital Readmissions Analytics Dashboard

An analytics project exploring hospital encounters and 30-day
readmission patterns using Python, PostgreSQL, and Power BI.

## Project Overview

This project analyzes the UCI Diabetes 130-US Hospitals dataset, which
contains hospital encounter records from 1999--2008. The goal is to
summarize encounter volume, readmissions, length of stay, medication
use, and patterns across selected encounter characteristics.

## Tools and Technologies

-   **Python:** data inspection and cleaning with Pandas
-   **PostgreSQL:** storing and validating cleaned encounter data
-   **Power BI:** interactive dashboard, KPI cards, charts, and slicers
-   **DAX / Power BI aggregations:** summary metrics and
    readmission-rate visuals

## Data Preparation

The original dataset contained **101,766 encounters**. Records with
discharge disposition IDs `11`, `13`, `14`, `19`, `20`, and `21` were
excluded, leaving **99,343 encounters** for analysis.

A binary field, `readmitted_30d`, was created: - `1` when the original
readmission value was `<30` - `0` otherwise

The cleaned data contains 99,343 unique encounter IDs. Multiple
encounters for the same patient are retained because this is an
encounter-level analysis.

## Dashboard KPIs

  KPI                                       Value
  ----------------------------------- -----------
  Total encounters                         99,343
  30-day readmission rate                  11.39%
  Average length of stay                4.38 days
  Average medications per encounter         15.98

Values may display with abbreviated formatting in Power BI (for example,
`99.343K`).

## Dashboard Visuals

The report includes charts exploring 30-day readmission rates by: -
Admission type - Gender - Length of stay - Age group - Previous
inpatient visits - Previous emergency visits

It also includes average length of stay by medical specialty and slicers
for age, admission type, and gender.

## Repository Structure

``` text
hospital-readmissions-dashboard/
├── data/
│   ├── raw/
│   └── processed/
├── reports/
│   └── validation_report.json
├── scripts/
│   ├── inspect_data.py
│   ├── clean_data.py
│   └── load_data.py
├── screenshots/
│   └── dashboard.png
├── .gitignore
└── Hospital_Readmissions_Dashboard.pbix
```

This is an example of the intended project organization. Keep raw data,
credentials, and other restricted files out of public GitHub
repositories.

## How to Reproduce

1.  Download the UCI Diabetes 130-US Hospitals dataset and place the
    source CSV files in `data/raw/`.
2.  Create and activate a Python virtual environment.
3.  Install the Python dependencies required by the scripts.
4.  Configure local PostgreSQL connection settings in a `.env` file.
5.  Run the data inspection and cleaning scripts.
6.  Run the loading script to import the cleaned data into PostgreSQL.
7.  Open `Hospital_Readmissions_Dashboard.pbix` in Power BI Desktop and
    connect it to the local PostgreSQL table as configured for your
    environment.

Use the project's actual dependency file and script instructions if
available.

## Limitations

-   The dataset represents historical U.S. hospital encounters from
    **1999--2008**; results should not be treated as a picture of
    current hospital performance.
-   This is observational analysis. Associations shown in charts do not
    establish that a factor causes readmission.
-   The 30-day readmission measure is defined from the dataset's `<30`
    category; all other original categories are coded as `0` for this
    project.
-   Findings depend on the data cleaning decisions described above.

## Screenshot

Save the final Power BI screenshot at `screenshots/dashboard.png` and
embed it here:

``` markdown
![Hospital Readmissions Analytics Dashboard](screenshots/dashboard.png)
```

## Data Source

UCI Machine Learning Repository --- **Diabetes 130-US Hospitals for
Years 1999--2008**.
