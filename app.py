import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(
    page_title="COVID-19 Data Explorer",
    layout="wide"
)

st.title("COVID-19 Data Explorer")
st.write("Explore global COVID-19 trends interactively.")

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parents[1]
DATA_PATH = PROJECT_ROOT / "DataCleaning" / "compact_clean.csv"
CASES_IMAGE_PATH = APP_DIR / "daily_new_cases_trend.png"
DEATHS_IMAGE_PATH = APP_DIR / "daily_new_deaths_trend.png"
CASES_DEATHS_IMAGE_PATH = APP_DIR / "cases_vs_deaths_united_states.png"

if not DATA_PATH.exists():
    st.error(f"compact_clean.csv was not found at {DATA_PATH}")
    st.stop()

df = pd.read_csv(DATA_PATH)
df["date"] = pd.to_datetime(df["date"])


def save_default_trend_images(data):
    default_countries = [
        country
        for country in ["United States", "United Kingdom", "India", "Germany", "France", "Canada"]
        if country in set(data["country"].dropna())
    ]
    export_df = data[data["country"].isin(default_countries)].copy()
    sns.set_theme(style="whitegrid")

    fig_static, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(
        data=export_df,
        x="date",
        y="new_cases_smoothed_per_million",
        hue="country",
        ax=ax,
    )
    ax.set_title("Daily New Confirmed COVID-19 Cases per Million People")
    ax.set_xlabel("Date")
    ax.set_ylabel("New cases per million people")
    fig_static.tight_layout()
    fig_static.savefig(CASES_IMAGE_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig_static)

    fig_static, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(
        data=export_df,
        x="date",
        y="new_deaths_smoothed_per_million",
        hue="country",
        ax=ax,
    )
    ax.set_title("Daily New Confirmed COVID-19 Deaths per Million People")
    ax.set_xlabel("Date")
    ax.set_ylabel("New deaths per million people")
    fig_static.tight_layout()
    fig_static.savefig(DEATHS_IMAGE_PATH, dpi=300, bbox_inches="tight")
    plt.close(fig_static)

    if "United States" in default_countries:
        us_df = data[data["country"] == "United States"].copy()
        fig_static, ax = plt.subplots(figsize=(12, 6))
        ax.plot(us_df["date"], us_df["new_cases_smoothed_per_million"], label="New cases")
        ax.plot(us_df["date"], us_df["new_deaths_smoothed_per_million"], label="New deaths")
        ax.set_title("COVID-19 Cases and Deaths Trend in United States")
        ax.set_xlabel("Date")
        ax.set_ylabel("Value per million people")
        ax.legend()
        fig_static.tight_layout()
        fig_static.savefig(CASES_DEATHS_IMAGE_PATH, dpi=300, bbox_inches="tight")
        plt.close(fig_static)


save_default_trend_images(df)

countries = sorted(df["country"].dropna().unique())

selected_countries = st.multiselect(
    "Select countries:",
    countries,
    default=[
        "United States",
        "United Kingdom",
        "India",
        "Germany",
        "France",
        "Canada"
    ]
)

if not selected_countries:
    st.warning("Please select at least one country.")
    st.stop()

filtered_df = df[df["country"].isin(selected_countries)].copy()

chart_type = st.selectbox(
    "Select chart:",
    [
        "Daily New Cases Trend",
        "Daily New Deaths Trend",
        "Cases vs Deaths (Single Country)"
    ]
)

if chart_type == "Daily New Cases Trend":

    fig = px.line(
        filtered_df,
        x="date",
        y="new_cases_smoothed_per_million",
        color="country",
        title="Daily New Confirmed COVID-19 Cases per Million People",
        labels={
            "date": "Date",
            "new_cases_smoothed_per_million": "New cases per million people",
            "country": "Country"
        },
        hover_data={
            "country": True,
            "date": True,
            "new_cases_smoothed_per_million": ":.2f"
        }
    )

elif chart_type == "Daily New Deaths Trend":

    fig = px.line(
        filtered_df,
        x="date",
        y="new_deaths_smoothed_per_million",
        color="country",
        title="Daily New Confirmed COVID-19 Deaths per Million People",
        labels={
            "date": "Date",
            "new_deaths_smoothed_per_million": "New deaths per million people",
            "country": "Country"
        },
        hover_data={
            "country": True,
            "date": True,
            "new_deaths_smoothed_per_million": ":.2f"
        }
    )

elif chart_type == "Cases vs Deaths (Single Country)":

    one_country = st.selectbox(
        "Select one country:",
        selected_countries
    )

    single_df = filtered_df[filtered_df["country"] == one_country].copy()

    fig = px.line(
        single_df,
        x="date",
        y=[
            "new_cases_smoothed_per_million",
            "new_deaths_smoothed_per_million"
        ],
        title=f"COVID-19 Cases and Deaths Trend in {one_country}",
        labels={
            "date": "Date",
            "value": "Value per million people",
            "variable": "Indicator"
        }
    )

fig.update_layout(
    hovermode="x unified",
    xaxis=dict(
        rangeslider=dict(visible=True),
        type="date"
    ),
    height=600
)

st.plotly_chart(fig, use_container_width=True)
