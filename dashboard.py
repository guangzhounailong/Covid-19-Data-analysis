from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="COVID-19 Global Analysis", layout="wide")

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "DataCleaning" / "compact_clean.csv"
INSIGHTS = ROOT / "Insights"
ML = ROOT / "ML_mortality_risk"

TIME_DIR = INSIGHTS / "COVID-19_time"
COUNTRY_DIR = INSIGHTS / "Countries_compare"
VACCINE_DIR = INSIGHTS / "Countries_vaccinationCoverage"
POP_DIR = INSIGHTS / "Population&Spread"
VAC_MORT_DIR = INSIGHTS / "Vaccination_mortality"


st.markdown(
    """
    <style>
    :root {
        --primary: #0066cc;
        --primary-dark: #2997ff;
        --ink: #1d1d1f;
        --muted: #6e6e73;
        --hairline: #e0e0e0;
        --paper: #ffffff;
        --parchment: #f5f5f7;
        --pearl: #fafafc;
        --dark: #272729;
        --dark-2: #2a2a2c;
    }

    .stApp {
        background: var(--paper);
        color: var(--ink);
        font-family: "SF Pro Text", "SF Pro Display", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    header[data-testid="stHeader"] {
        background: rgba(0, 0, 0, .88);
        backdrop-filter: saturate(180%) blur(14px);
    }

    .block-container {
        max-width: 1160px;
        padding: 2.6rem 1.25rem 4rem;
    }

    #MainMenu, footer { visibility: hidden; }

    h1, h2, h3, p {
        letter-spacing: 0;
    }

    h1 {
        margin: 0;
        font-size: 3.55rem;
        line-height: 1.05;
        font-weight: 650;
    }

    h2 {
        margin: 0;
        font-size: 2.18rem;
        line-height: 1.12;
        font-weight: 650;
    }

    h3 {
        font-size: 1.08rem;
        line-height: 1.26;
        font-weight: 650;
    }

    .hero {
        margin: 0 0 2rem;
        padding: 4.2rem 3.2rem 3.3rem;
        background: var(--dark);
        color: #ffffff;
        text-align: center;
    }

    .hero .kicker,
    .section-kicker,
    .figure-label {
        margin-bottom: .8rem;
        color: var(--primary-dark);
        font-size: .78rem;
        font-weight: 700;
        letter-spacing: .08em;
        text-transform: uppercase;
    }

    .hero p {
        max-width: 790px;
        margin: 1.1rem auto 0;
        color: #cccccc;
        font-size: 1.28rem;
        line-height: 1.48;
    }

    .metric-strip {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        border-top: 1px solid var(--hairline);
        border-bottom: 1px solid var(--hairline);
        margin: 2rem 0 0;
        background: #ffffff;
    }

    .metric {
        padding: 1.05rem 1.1rem;
        border-right: 1px solid var(--hairline);
    }

    .metric:last-child { border-right: 0; }

    .metric span {
        display: block;
        color: var(--muted);
        font-size: .82rem;
        line-height: 1.3;
    }

    .metric strong {
        display: block;
        margin-top: .4rem;
        font-size: 1.28rem;
        font-weight: 650;
        line-height: 1.1;
    }

    .report-band {
        margin: 2.2rem 0;
        padding: 2.3rem;
        background: var(--parchment);
    }

    .report-band.dark {
        background: var(--dark-2);
        color: #ffffff;
    }

    .report-band.dark p,
    .report-band.dark li,
    .report-band.dark .body-muted {
        color: #cccccc;
    }

    .two-col {
        display: grid;
        grid-template-columns: minmax(0, .9fr) minmax(0, 1.1fr);
        gap: 2rem;
        align-items: start;
    }

    .three-col {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1px;
        background: var(--hairline);
        border: 1px solid var(--hairline);
    }

    .brief-cell {
        min-height: 170px;
        padding: 1.2rem;
        background: #ffffff;
    }

    .brief-cell strong {
        display: block;
        margin: .85rem 0 .35rem;
        font-size: 1rem;
    }

    .brief-cell p,
    .section-copy p,
    .finding p {
        margin: 0;
        color: #55555a;
        font-size: .98rem;
        line-height: 1.56;
    }

    .method-list {
        margin: 1.2rem 0 0;
        padding-left: 1.1rem;
        color: #55555a;
        line-height: 1.62;
    }

    .insight-index {
        color: var(--primary);
        font-size: .86rem;
        font-weight: 700;
    }

    .section-title {
        margin: .5rem 0 .95rem;
    }

    .finding {
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid var(--hairline);
    }

    .finding strong {
        display: block;
        margin-bottom: .35rem;
        font-size: .86rem;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: .05em;
    }

    .dark .finding {
        border-color: rgba(255, 255, 255, .18);
    }

    .dark .finding strong {
        color: #cccccc;
    }

    .dark .section-kicker {
        color: var(--primary-dark);
    }

    .figure-frame {
        padding: .65rem;
        background: #ffffff;
        border: 1px solid var(--hairline);
    }

    div[data-testid="stImage"] img {
        background: #ffffff;
        border: 1px solid var(--hairline);
        border-radius: 0;
    }

    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid var(--hairline);
        padding: .9rem 1rem;
    }

    .model-metrics {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1rem;
        margin: 0 0 1.5rem;
    }

    .model-metric {
        min-width: 0;
        padding: 1.1rem 1.25rem;
        background: #ffffff;
        border: 1px solid var(--hairline);
    }

    .model-metric span {
        display: block;
        margin-bottom: .55rem;
        color: #3f3f46;
        font-size: .95rem;
        line-height: 1.3;
    }

    .model-metric strong {
        display: block;
        color: #30303a;
        font-size: 2.05rem;
        font-weight: 500;
        line-height: 1.12;
        overflow-wrap: anywhere;
        word-break: normal;
    }

    .model-metric strong.text-value {
        font-size: 1.85rem;
        line-height: 1.16;
        white-space: normal;
    }

    div[data-testid="stTabs"] button {
        font-size: .92rem;
    }

    .caption {
        margin-top: .5rem;
        color: var(--muted);
        font-size: .86rem;
        line-height: 1.42;
    }

    @media (max-width: 860px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        h1 { font-size: 2.35rem; }
        h2 { font-size: 1.7rem; }

        .hero {
            padding: 3rem 1.25rem 2.4rem;
        }

        .hero p {
            font-size: 1.05rem;
        }

        .metric-strip,
        .model-metrics,
        .two-col,
        .three-col {
            grid-template-columns: 1fr;
        }

        .metric {
            border-right: 0;
            border-bottom: 1px solid var(--hairline);
        }

        .metric:last-child {
            border-bottom: 0;
        }

        .report-band {
            padding: 1.45rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    cols = [
        "country",
        "date",
        "code",
        "continent",
        "total_cases",
        "total_deaths",
        "new_cases_smoothed_per_million",
        "new_deaths_smoothed_per_million",
        "people_vaccinated_per_hundred",
        "people_fully_vaccinated_per_hundred",
        "gdp_per_capita",
    ]
    data = pd.read_csv(DATA_PATH, usecols=lambda col: col in cols)
    data["date"] = pd.to_datetime(data["date"])
    return data


@st.cache_data(show_spinner=False)
def latest_rows(data: pd.DataFrame) -> pd.DataFrame:
    return data.sort_values("date").groupby("country", as_index=False).last()


@st.cache_data(show_spinner=False)
def model_metrics() -> pd.DataFrame:
    path = ML / "results" / "model_metrics.csv"
    return pd.read_csv(path) if path.exists() else pd.DataFrame()


def image(path: Path, caption: str) -> None:
    if path.exists():
        st.image(str(path), caption=caption, use_container_width=True)
    else:
        st.warning(f"Missing file: {path.relative_to(ROOT)}")


def map_chart(data: pd.DataFrame, column: str, title: str, label: str, color_scale: str) -> None:
    map_data = data[["country", "code", column]].dropna()
    fig = px.choropleth(
        map_data,
        locations="code",
        color=column,
        hover_name="country",
        color_continuous_scale=color_scale,
        labels={column: label},
        title=title,
    )
    fig.update_layout(
        height=610,
        margin=dict(l=0, r=0, t=54, b=0),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font=dict(color="#1d1d1f", size=13),
        geo=dict(showframe=False, showcoastlines=True, projection_type="natural earth"),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def section_intro(index: str, title: str, question: str, interpretation: str, dark: bool = False) -> None:
    band_class = "report-band dark" if dark else "report-band"
    st.markdown(
        f"""
        <section class="{band_class}">
          <div class="section-kicker">Insight {index}</div>
          <h2 class="section-title">{title}</h2>
          <div class="finding">
            <strong>Research question</strong>
            <p>{question}</p>
          </div>
          <div class="finding">
            <strong>Interpretation</strong>
            <p>{interpretation}</p>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


if not DATA_PATH.exists():
    st.error(f"Missing data file: {DATA_PATH}")
    st.stop()


df = load_data()
latest_df = latest_rows(df)
metrics_df = model_metrics()
date_range = f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"

st.markdown(
    f"""
    <section class="hero">
      <div class="kicker">Academic Presentation Dashboard</div>
      <h1>COVID-19 Global Data Analysis</h1>
      <p>
        A concise research presentation of global COVID-19 spread, country-level impact,
        vaccination coverage, and mortality risk classification.
      </p>
    </section>
    <section class="metric-strip">
      <div class="metric"><span>Cleaned observations</span><strong>{len(df):,}</strong></div>
      <div class="metric"><span>Countries / locations</span><strong>{df["country"].nunique():,}</strong></div>
      <div class="metric"><span>Study period</span><strong>{df["date"].min().year}-{df["date"].max().year}</strong></div>
      <div class="metric"><span>Core insights</span><strong>5</strong></div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="report-band">
      <div class="two-col">
        <div>
          <div class="section-kicker">Research Brief</div>
          <h2>From descriptive trends to mortality risk modeling.</h2>
        </div>
        <div class="section-copy">
          <p>
            This dashboard is structured as a presentation report rather than a general-purpose tool.
            Each section states a research question, shows the supporting evidence, and gives a short
            interpretation for discussion.
          </p>
          <ul class="method-list">
            <li>Data source: cleaned compact COVID-19 dataset.</li>
            <li>Analysis scope: time trends, country comparison, population spread, vaccination coverage, and mortality.</li>
            <li>Modeling task: country-level high mortality risk classification.</li>
          </ul>
        </div>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <section class="three-col">
      <div class="brief-cell">
        <span class="insight-index">Dataset</span>
        <strong>Validated country-date panel</strong>
        <p>{date_range}. Missing values, duplicates, and inconsistencies were handled before analysis.</p>
      </div>
      <div class="brief-cell">
        <span class="insight-index">Evidence</span>
        <strong>Five visual insight groups</strong>
        <p>Figures are reused from the project outputs to keep the presentation consistent with the analysis workflow.</p>
      </div>
      <div class="brief-cell">
        <span class="insight-index">Model</span>
        <strong>High mortality risk classification</strong>
        <p>Random Forest is compared against Logistic Regression using accuracy, F1 score, and ROC-AUC.</p>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

section_intro(
    "01",
    "COVID-19 Time Trend",
    "How did normalized daily cases and deaths evolve across representative countries?",
    "Per-million indicators make country trajectories comparable and reveal pandemic waves that would be hidden by raw totals.",
)

countries = sorted(df["country"].dropna().unique())
defaults = [c for c in ["United States", "United Kingdom", "India", "Germany", "France", "Canada"] if c in countries]
selected = st.multiselect("Countries for interactive trend chart", countries, default=defaults)
if selected:
    filtered = df[df["country"].isin(selected)]
    metric = st.selectbox(
        "Trend metric",
        ["Daily new cases per million", "Daily new deaths per million", "Cases vs deaths for one country"],
    )
    if metric == "Daily new cases per million":
        fig = px.line(
            filtered,
            x="date",
            y="new_cases_smoothed_per_million",
            color="country",
            labels={"new_cases_smoothed_per_million": "New cases per million", "date": "Date", "country": "Country"},
        )
    elif metric == "Daily new deaths per million":
        fig = px.line(
            filtered,
            x="date",
            y="new_deaths_smoothed_per_million",
            color="country",
            labels={"new_deaths_smoothed_per_million": "New deaths per million", "date": "Date", "country": "Country"},
        )
    else:
        country = st.selectbox("Country", selected)
        one = filtered[filtered["country"] == country]
        fig = px.line(
            one,
            x="date",
            y=["new_cases_smoothed_per_million", "new_deaths_smoothed_per_million"],
            labels={"value": "Value per million", "date": "Date", "variable": "Metric"},
        )
    fig.update_layout(height=520, hovermode="x unified", margin=dict(l=0, r=0, t=24, b=0), legend_title_text="")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

trend_col1, trend_col2 = st.columns(2)
with trend_col1:
    image(TIME_DIR / "daily_new_cases_trend.png", "Figure 1A. Daily new confirmed cases per million.")
with trend_col2:
    image(TIME_DIR / "daily_new_deaths_trend.png", "Figure 1B. Daily new confirmed deaths per million.")

section_intro(
    "02",
    "Country and Continent Comparison",
    "Which countries and continents show the largest cumulative burden?",
    "Country rankings identify concentrated impact, while the continent comparison supports a regional reading of case and death differences.",
    dark=True,
)

compare_col1, compare_col2 = st.columns(2)
with compare_col1:
    image(COUNTRY_DIR / "top_affected_countries.png", "Figure 2A. Top affected countries.")
with compare_col2:
    image(COUNTRY_DIR / "continent_comparison.png", "Figure 2B. Continent comparison.")

html_map = COUNTRY_DIR / "covid_world_map.html"
if html_map.exists():
    st.markdown('<div class="figure-label">Interactive evidence</div>', unsafe_allow_html=True)
    components.html(html_map.read_text(encoding="utf-8"), height=620, scrolling=False)

section_intro(
    "03",
    "Population and Spread",
    "How does population scale relate to COVID-19 spread?",
    "The log-scale view prevents large-population countries from visually dominating the analysis and makes cross-country spread patterns easier to compare.",
)

image(POP_DIR / "log_plot_final.png", "Figure 3. Population size and COVID-19 spread on a log-scale plot.")

section_intro(
    "04",
    "GDP and Vaccination Coverage",
    "How are vaccination coverage and GDP per capita distributed across countries?",
    "The evidence combines regression-style comparison, continental distribution, and geographic maps to show inequality in vaccination access and completion.",
    dark=True,
)

gdp_col1, gdp_col2 = st.columns(2)
with gdp_col1:
    image(VACCINE_DIR / "gdp_vaccination_coverage.png", "Figure 4A. GDP per capita vs vaccination coverage.")
with gdp_col2:
    image(VACCINE_DIR / "vaccination_coverage_by_continent.png", "Figure 4B. Vaccination coverage by continent.")

st.markdown('<div class="figure-label">Geographic distribution</div>', unsafe_allow_html=True)
map_tab1, map_tab2, map_tab3 = st.tabs(["At least one dose", "Full vaccination", "GDP per capita"])
with map_tab1:
    map_chart(
        latest_df,
        "people_vaccinated_per_hundred",
        "COVID-19 Vaccination Coverage (at least one dose) per hundred people",
        "Vaccinated per 100",
        "Viridis",
    )
with map_tab2:
    map_chart(
        latest_df,
        "people_fully_vaccinated_per_hundred",
        "Full Vaccination Coverage (completed primary series) per hundred people",
        "Fully vaccinated per 100",
        "Plasma",
    )
with map_tab3:
    map_chart(latest_df, "gdp_per_capita", "GDP per capita (USD)", "GDP per capita", "Blues")

section_intro(
    "05",
    "Vaccination and Mortality",
    "What relationship appears between vaccination coverage and mortality indicators?",
    "The regression view provides a direct visual basis for discussing whether higher vaccination coverage is associated with lower mortality burden.",
)

image(VAC_MORT_DIR / "vaccination_vs_mortality_regression.png", "Figure 5. Vaccination coverage and mortality regression.")

st.markdown(
    """
    <section class="report-band dark">
      <div class="section-kicker">Model Validation</div>
      <h2 class="section-title">High Mortality Risk Classification</h2>
      <div class="finding">
        <strong>Purpose</strong>
        <p>
          The machine learning component converts descriptive country-level indicators into a classification task:
          identifying countries with high COVID-19 mortality risk.
        </p>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

if not metrics_df.empty:
    best = metrics_df.sort_values("f1", ascending=False).iloc[0]
    st.markdown(
        f"""
        <section class="model-metrics">
          <div class="model-metric">
            <span>Best model</span>
            <strong class="text-value">{best["model"]}</strong>
          </div>
          <div class="model-metric">
            <span>Accuracy</span>
            <strong>{best["accuracy"]:.2f}</strong>
          </div>
          <div class="model-metric">
            <span>F1 score</span>
            <strong>{best["f1"]:.2f}</strong>
          </div>
          <div class="model-metric">
            <span>ROC-AUC</span>
            <strong>{best["roc_auc"]:.2f}</strong>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

model_col1, model_col2 = st.columns(2)
with model_col1:
    image(ML / "outputs" / "model_metrics_comparison.png", "Figure 6A. Model metrics comparison.")
    image(ML / "outputs" / "roc_curve.png", "Figure 6B. ROC curve.")
with model_col2:
    image(ML / "outputs" / "feature_importance.png", "Figure 6C. Feature importance.")
    image(ML / "outputs" / "risk_distribution_by_continent.png", "Figure 6D. Risk distribution by continent.")

st.markdown(
    """
    <section class="report-band">
      <div class="section-kicker">Conclusion</div>
      <h2 class="section-title">Key Takeaway</h2>
      <div class="section-copy">
        <p>
          The analysis shows that COVID-19 impact cannot be explained by a single factor.
          Time dynamics, regional differences, population scale, vaccination coverage, GDP context,
          and health-related predictors jointly shape mortality risk.
        </p>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)
