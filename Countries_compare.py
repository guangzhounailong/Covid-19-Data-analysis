import pandas as pd
import plotly.express as px
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 读取数据
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parents[1]
DATA_PATH = PROJECT_ROOT / "DataCleaning" / "compact_clean.csv"
CONTINENT_IMAGE_PATH = SCRIPT_DIR / "continent_comparison.png"
COUNTRY_IMAGE_PATH = SCRIPT_DIR / "top_affected_countries.png"

df = pd.read_csv(DATA_PATH)
df['date'] = pd.to_datetime(df['date'])

# 2. 过滤掉非国家行（如 'World', 'Asia' 等聚合行通常 code 为空或特殊值）
df = df[df['code'].notna() & (df['code'].str.len() == 3)]

# 3. 按月份聚合（取每月最后一天的累计值）
df['year_month'] = df['date'].dt.to_period('M').astype(str)
monthly = (df.sort_values('date')
             .groupby(['country', 'code', 'continent', 'year_month'], as_index=False)
             .agg({
                 'total_cases_per_million': 'last',
                 'total_deaths_per_million': 'last'
             }))

# 4. 处理缺失值
monthly['total_cases_per_million'] = monthly['total_cases_per_million'].fillna(0)
monthly['total_deaths_per_million'] = monthly['total_deaths_per_million'].fillna(0)

# 5. 制作带时间滑块的世界地图（病例数）
fig = px.choropleth(
    monthly.sort_values('year_month'),
    locations='code',
    color='total_cases_per_million',
    hover_name='country',
    hover_data={'total_deaths_per_million': ':.1f', 'continent': True},
    animation_frame='year_month',
    color_continuous_scale='Reds',                # 越严重越深
    range_color=(0, monthly['total_cases_per_million'].quantile(0.95)),
    projection='natural earth',
    title='The cumulative confirmed cases of COVID-19 worldwide (per million people) over time'
)

fig.update_layout(
    coloraxis_colorbar=dict(title='Cases / Million'),
    height=600
)
latest = (
    df.sort_values("date")
    .groupby(["country", "code", "continent"], as_index=False)
    .last()
)

continent_summary = (
    latest.groupby("continent", as_index=False)
    .agg(
        total_cases=("total_cases_per_million", "mean"),
        total_deaths=("total_deaths_per_million", "mean"),
    )
    .sort_values("total_deaths", ascending=False)
)

sns.set_theme(style="whitegrid")
fig_static, axes = plt.subplots(1, 2, figsize=(14, 6))
sns.barplot(
    data=continent_summary,
    x="total_cases",
    y="continent",
    ax=axes[0],
    color="#4C78A8",
)
axes[0].set_title("Average Total Cases per Million by Continent")
axes[0].set_xlabel("Cases per million")
axes[0].set_ylabel("")

sns.barplot(
    data=continent_summary,
    x="total_deaths",
    y="continent",
    ax=axes[1],
    color="#D55E00",
)
axes[1].set_title("Average Total Deaths per Million by Continent")
axes[1].set_xlabel("Deaths per million")
axes[1].set_ylabel("")
fig_static.tight_layout()
fig_static.savefig(CONTINENT_IMAGE_PATH, dpi=300, bbox_inches="tight")
plt.close(fig_static)

top_countries = latest.nlargest(15, "total_cases_per_million")
fig_static, ax = plt.subplots(figsize=(11, 7))
sns.barplot(
    data=top_countries,
    x="total_cases_per_million",
    y="country",
    hue="continent",
    dodge=False,
    ax=ax,
)
ax.set_title("Top 15 Countries by Total Cases per Million")
ax.set_xlabel("Cases per million")
ax.set_ylabel("")
ax.legend(title="Continent", loc="lower right")
fig_static.tight_layout()
fig_static.savefig(COUNTRY_IMAGE_PATH, dpi=300, bbox_inches="tight")
plt.close(fig_static)
