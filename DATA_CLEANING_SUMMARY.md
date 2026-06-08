# Data Cleaning Summary

This document summarizes the updated data exploration and cleaning workflow for the COVID-19 `compact.csv` dataset. It is aligned with the course requirement to load the data, explore its structure, check missing values, duplicates, and inconsistencies, clean the dataset, and validate the cleaned output.

## Files

- Raw dataset: `../dataset/compact.csv`
- Cleaning notebook: `datacleaning.ipynb`
- Cleaned dataset: `compact_clean.csv`
- Missing-value summary: `missing_data.csv`
- Descriptive statistics: `description.csv`
- Country-level files from earlier project work: `country/`

## 1. Loading the Dataset

The notebook loads the dataset with pandas:

```python
df = pd.read_csv(data_path)
```

The path logic checks common project locations so the notebook can run from either the `DataCleaning` folder or the project root. The initial dataset shape is printed after loading.

## 2. Initial Data Exploration

The notebook keeps the original exploration steps:

- `df.info()` to inspect rows, columns, data types, and non-null counts.
- `df.describe()` to summarize numeric variables.
- `df.isnull().sum()` and `df.isnull().mean()` to inspect missing values.
- `df.duplicated().sum()` to check full-row duplicates.

The descriptive statistics are saved to:

```text
description.csv
```

## 3. Missing-Value Summary

The notebook now creates a sorted missing-value summary table with:

- `missing_count`
- `missing_ratio_%`

The table is sorted from highest to lowest missing ratio and saved to:

```text
missing_data.csv
```

This makes it easier to identify columns with serious data availability issues.

## 4. High-Missing Columns

The notebook creates:

```python
high_missing_cols
```

This variable stores columns with more than 50% missing values.

Most of these columns are removed from the cleaned dataset and are not used in later EDA, visualization, or modeling. The reason is that more than half of their observations are missing, so they are not reliable enough for the core analysis.

Three vaccination rate columns are retained as explicit exceptions:

```text
people_vaccinated_per_hundred
people_fully_vaccinated_per_hundred
total_vaccinations_per_hundred
```

These fields are kept because vaccination coverage is an important topic for later EDA and visualization. A separate check of the original dataset showed that many countries have these fields, but the values are not continuous daily records for most countries. Therefore, they are retained for vaccination-related insights but should be interpreted carefully.

One fully empty column is removed:

```text
human_development_index
```

It is removed because the column contains no usable data in this dataset.

## 5. Further Inconsistency and Anomaly Checks

The notebook adds a new section named:

```text
Further Inconsistency and Anomaly Checks
```

It checks and prints:

- Invalid dates after converting `date` with `pd.to_datetime(errors="coerce")`.
- Duplicate `country + date` records.
- Numeric columns that contain negative values.
- Rows where `total_deaths > total_cases`.
- Rows where `new_deaths > new_cases`.
- Rows where `positive_rate` is outside the range `[0, 1]`.
- Rows where `reproduction_rate` is negative.

All checks are guarded by column-existence tests to avoid `KeyError`.

## 6. Missing-Value Cleaning Logic

The notebook no longer fills all core case and death fields with zero in one step.

First, the data is sorted by:

```python
df = df.sort_values(["country", "date"])
```

Cumulative columns are forward-filled within each country:

```text
total_cases
total_deaths
total_cases_per_million
total_deaths_per_million
```

After forward filling, any remaining missing values in these cumulative columns are filled with 0.

Daily new-value columns are filled with 0:

```text
new_cases
new_deaths
new_cases_per_million
new_deaths_per_million
```

This separates cumulative time-series logic from daily reporting logic.

## 7. Duplicate Handling

The notebook checks:

- Full-row duplicates.
- Duplicate records based on `country + date`.

If duplicate `country + date` records exist, the notebook keeps the first record:

```python
df = df.drop_duplicates(subset=["country", "date"], keep="first")
```

If no duplicates are found, the notebook still prints the result for documentation.

## 8. Validation After Cleaning

The notebook adds a final validation section named:

```text
Validation After Cleaning
```

It prints:

- Cleaned data shape.
- Top 20 columns by remaining missing values.
- Number of full-row duplicates after cleaning.
- Number of `country + date` duplicates after cleaning.
- Final `date` data type.
- Whether `total_deaths > total_cases` still exists.
- Whether `positive_rate` still has values outside `[0, 1]`.

This section helps show that the cleaning process was completed and that remaining issues are documented.

## 9. Saving the Cleaned Dataset

The final cleaned dataset is saved with:

```python
df.to_csv("compact_clean.csv", index=False)
```

The output file is:

```text
compact_clean.csv
```

## 10. Splitting the Cleaned Dataset by Country

After saving `compact_clean.csv`, the notebook also splits the cleaned dataset into separate CSV files based on the `country` column.

The output folder is:

```text
country/
```

The notebook creates the folder if it does not already exist, then writes one file per country or region. For example:

```text
Afghanistan.csv
Albania.csv
United_States.csv
World.csv
```

Reason for this step:

- The dataset is a country-level time-series dataset.
- Splitting by `country` makes it easier to inspect one country at a time.
- Smaller country files are more convenient for later analysis, presentation, or country-specific visualization.
- This step keeps the full cleaned dataset while also providing country-level subsets for focused analysis.

The country-level files are generated from the cleaned dataframe, so they follow the same cleaning rules as `compact_clean.csv`: most columns with more than 50% missing values are removed, while the three selected vaccination rate columns are retained for later analysis.

## Course Requirement Mapping

| Course requirement | Notebook update |
| --- | --- |
| Load the dataset into Python | Loads `compact.csv` with pandas and prints initial shape. |
| Perform initial exploration | Keeps `info`, `describe`, missing-value checks, and duplicate checks. |
| Check missing values, duplicates, and inconsistencies | Adds sorted missing summary, high-missing columns, invalid dates, duplicate country-date records, negative values, and impossible relationships. |
| Clean the dataset | Removes most columns with more than 50% missing values, retains three selected vaccination rate columns, removes fully empty columns, handles cumulative and daily missing values separately, and removes duplicate country-date records if present. |
| Validate and save results | Adds final validation checks, saves `compact_clean.csv`, and exports country-level CSV files. |
