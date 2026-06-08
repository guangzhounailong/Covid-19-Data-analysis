# COVID-19 Global Analysis Dashboard

This project analyzes global COVID-19 data through cleaned datasets, exploratory visualizations, and a mortality-risk machine learning model. The main entry point is a Streamlit dashboard that brings together the project outputs from data cleaning, insights, and modeling.

## Project Structure

```text
Final_draft_Gp06/
|-- dashboard.py
|-- DataCleaning/
|   |-- compact_clean.csv
|   |-- datacleaning.ipynb
|   |-- DATA_CLEANING_SUMMARY.md
|   `-- country/
|-- Insights/
|   |-- Countries_compare/
|   |-- Countries_vaccinationCoverage/
|   |-- COVID-19_time/
|   |-- Population&Spread/
|   `-- Vaccination_mortality/
`-- ML_mortality_risk/
    |-- mortality_risk_classification.py
    |-- outputs/
    `-- results/
```

## Requirements

Use Python 3.10 or newer. The project uses these Python packages:

- `pandas`
- `numpy`
- `streamlit`
- `plotly`
- `matplotlib`
- `seaborn`
- `scikit-learn`
- `jupyter` or `notebook` if you want to run the notebooks

## Setup

1. Open a terminal in the project folder:

   ```bash
   cd "D:\Data Programming Workshop\Final_draft_Gp06"
   ```

2. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate the virtual environment.

   On Windows PowerShell:

   ```bash
   .venv\Scripts\Activate.ps1
   ```

   On Command Prompt:

   ```bash
   .venv\Scripts\activate.bat
   ```

   On macOS or Linux:

   ```bash
   source .venv/bin/activate
   ```

4. Install the required packages:

   ```bash
   pip install pandas numpy streamlit plotly matplotlib seaborn scikit-learn jupyter
   ```

## Run the Dashboard

From the project root, run:

```bash
streamlit run dashboard.py
```

Streamlit will print a local URL, usually:

```text
http://localhost:8501
```

Open that URL in your browser to view the dashboard.

## Regenerate Outputs

The repository already includes the cleaned dataset and generated figures used by the dashboard. If you want to regenerate selected outputs, run the scripts below from the project root.

Regenerate country comparison figures:

```bash
python Insights\Countries_compare\Countries_compare.py
```

Regenerate mortality-risk model results and figures:

```bash
python ML_mortality_risk\mortality_risk_classification.py
```

Run the interactive COVID-19 time explorer:

```bash
streamlit run Insights\COVID-19_time\app.py
```

To rerun the data-cleaning or notebook-based analysis steps, open the notebooks in Jupyter:

```bash
jupyter notebook
```

Then run the notebooks inside `DataCleaning/` and `Insights/`.

## Data Notes

- The dashboard expects the cleaned dataset at `DataCleaning/compact_clean.csv`.
- The dashboard also uses image and HTML outputs stored in `Insights/` and `ML_mortality_risk/`.
- Keep the folder structure unchanged when running the project, because the scripts use relative paths to locate data and output files.

## Troubleshooting

- If `streamlit` is not recognized, make sure the virtual environment is activated and the packages were installed successfully.
- If a file-not-found error appears, confirm you are running commands from the project root folder.
- If a notebook cannot find the raw dataset, check the path notes in `DataCleaning/DATA_CLEANING_SUMMARY.md`.
