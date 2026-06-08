from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.inspection import permutation_importance
from sklearn.preprocessing import OneHotEncoder, StandardScaler


DATA_PATH = Path("DataCleaning") / "compact_clean.csv"
OUTPUT_DIR = Path("ML_mortality_risk") / "outputs"
RESULTS_DIR = Path("ML_mortality_risk") / "results"
OUTPUT_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

RANDOM_STATE = 42
RISK_PALETTE = {
    "Low/Medium Risk": "#4C78A8",
    "High Risk": "#D55E00",
}

plt.style.use("seaborn-v0_8-whitegrid")
plt.rcParams.update(
    {
        "figure.dpi": 120,
        "savefig.dpi": 400,
        "font.family": "DejaVu Sans",
        "font.size": 10,
        "axes.titlesize": 12,
        "axes.labelsize": 10,
        "axes.titleweight": "bold",
        "legend.fontsize": 9,
        "legend.title_fontsize": 9,
        "xtick.labelsize": 9,
        "ytick.labelsize": 9,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.edgecolor": "#333333",
        "grid.color": "#D9D9D9",
        "grid.linewidth": 0.7,
    }
)


def save_figure(fig, filename):
    fig.savefig(OUTPUT_DIR / f"{filename}.png", bbox_inches="tight")
    plt.close(fig)


def clean_feature_name(feature):
    readable_names = {
        "people_fully_vaccinated_per_hundred": "Full vaccination rate",
        "gdp_per_capita": "GDP per capita",
        "median_age": "Median age",
        "life_expectancy": "Life expectancy",
        "population_density": "Population density",
        "diabetes_prevalence": "Diabetes prevalence",
        "hospital_beds_per_thousand": "Hospital beds per thousand",
        "continent": "Continent",
    }
    if feature.startswith("continent_"):
        return "Continent: " + feature.replace("continent_", "")
    return readable_names.get(feature, feature)


def last_non_null(series):
    """Return the last available value in a country time series."""
    non_null = series.dropna()
    if non_null.empty:
        return np.nan
    return non_null.iloc[-1]


def build_country_level_dataset(data_path):
    df = pd.read_csv(data_path, parse_dates=["date"])
    df = df.sort_values(["country", "date"])

    country_rows = []
    for country, group in df.groupby("country", sort=False):
        latest = group.iloc[-1]
        row = {
            "country": country,
            "continent": latest["continent"],
            "total_deaths_per_million": latest["total_deaths_per_million"],
            "people_fully_vaccinated_per_hundred": last_non_null(
                group["people_fully_vaccinated_per_hundred"]
            ),
            "people_vaccinated_per_hundred": last_non_null(
                group["people_vaccinated_per_hundred"]
            ),
            "total_vaccinations_per_hundred": last_non_null(
                group["total_vaccinations_per_hundred"]
            ),
            "gdp_per_capita": latest["gdp_per_capita"],
            "median_age": latest["median_age"],
            "life_expectancy": latest["life_expectancy"],
            "population_density": latest["population_density"],
            "diabetes_prevalence": latest["diabetes_prevalence"],
            "hospital_beds_per_thousand": latest["hospital_beds_per_thousand"],
        }
        country_rows.append(row)

    country_df = pd.DataFrame(country_rows)

    # Remove global/continent/income aggregates. The model should compare countries only.
    country_df = country_df.dropna(subset=["continent", "total_deaths_per_million"])

    high_risk_threshold = country_df["total_deaths_per_million"].quantile(0.75)
    country_df["mortality_risk"] = (
        country_df["total_deaths_per_million"] > high_risk_threshold
    ).astype(int)
    country_df["mortality_risk_label"] = country_df["mortality_risk"].map(
        {0: "Low/Medium Risk", 1: "High Risk"}
    )

    return country_df, high_risk_threshold


def make_models(numeric_features, categorical_features):
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipeline, numeric_features),
            ("cat", categorical_pipeline, categorical_features),
        ],
        verbose_feature_names_out=False,
    )

    logistic_model = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            (
                "model",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )

    random_forest_model = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=400,
                    max_depth=5,
                    min_samples_leaf=3,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )

    return {
        "Logistic Regression": logistic_model,
        "Random Forest": random_forest_model,
    }


def evaluate_model(name, model, x_train, x_test, y_train, y_test):
    model.fit(x_train, y_train)

    y_pred = model.predict(x_test)
    y_proba = model.predict_proba(x_test)[:, 1]

    metrics = {
        "model": name,
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "roc_auc": roc_auc_score(y_test, y_proba),
    }

    report = classification_report(
        y_test,
        y_pred,
        target_names=["Low/Medium Risk", "High Risk"],
        zero_division=0,
    )
    return metrics, report


def save_confusion_matrix(model, x_test, y_test):
    y_pred = model.predict(x_test)
    cm = confusion_matrix(y_test, y_pred)
    cm_percent = cm / cm.sum(axis=1, keepdims=True)
    annotations = np.empty_like(cm, dtype=object)
    for row in range(cm.shape[0]):
        for col in range(cm.shape[1]):
            annotations[row, col] = f"{cm[row, col]}\n({cm_percent[row, col]:.1%})"

    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    sns.heatmap(
        cm_percent,
        annot=annotations,
        fmt="",
        cmap="Blues",
        vmin=0,
        vmax=1,
        square=True,
        linewidths=0.8,
        linecolor="white",
        cbar_kws={"label": "Row-normalized share"},
        xticklabels=["Low/Medium Risk", "High Risk"],
        yticklabels=["Low/Medium Risk", "High Risk"],
        ax=ax,
    )
    ax.set_title("Confusion Matrix for Mortality Risk Classification")
    ax.set_xlabel("Predicted class")
    ax.set_ylabel("Observed class")
    ax.tick_params(axis="x", rotation=25)
    ax.tick_params(axis="y", rotation=0)
    fig.text(
        0.01,
        0.01,
        "Note: Cell labels show number of countries and row-normalized percentage.",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#555555",
    )
    save_figure(fig, "confusion_matrix")


def save_roc_curve(model, x_test, y_test):
    y_proba = model.predict_proba(x_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    auc = roc_auc_score(y_test, y_proba)

    fig, ax = plt.subplots(figsize=(6.2, 5.2))
    ax.plot(
        fpr,
        tpr,
        color="#0072B2",
        linewidth=2.4,
        label=f"Classifier ROC (AUC = {auc:.3f})",
    )
    ax.plot([0, 1], [0, 1], color="#666666", linestyle="--", linewidth=1.2, label="Random baseline")
    ax.fill_between(fpr, tpr, fpr, color="#0072B2", alpha=0.12)
    ax.set_title("Receiver Operating Characteristic Curve")
    ax.set_xlabel("False positive rate")
    ax.set_ylabel("True positive rate")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.02)
    ax.legend(loc="lower right", frameon=True)
    ax.grid(True, alpha=0.45)
    save_figure(fig, "roc_curve")


def save_feature_importance(model, top_n=10):
    feature_names = model.named_steps["preprocess"].get_feature_names_out()
    importances = model.named_steps["model"].feature_importances_

    importance_df = (
        pd.DataFrame(
            {
                "feature": feature_names,
                "feature_label": [clean_feature_name(feature) for feature in feature_names],
                "importance": importances,
            }
        )
        .sort_values("importance", ascending=False)
    )
    importance_df.to_csv(RESULTS_DIR / "feature_importance.csv", index=False)
    plot_df = importance_df.head(top_n).sort_values("importance", ascending=True)

    fig, ax = plt.subplots(figsize=(8.2, 5.3))
    ax.barh(
        plot_df["feature_label"],
        plot_df["importance"],
        color="#4C78A8",
        edgecolor="#222222",
        linewidth=0.4,
    )
    ax.set_title("Random Forest Feature Importance")
    ax.set_xlabel("Mean decrease in impurity")
    ax.set_ylabel("")
    ax.grid(axis="x", alpha=0.45)
    ax.grid(axis="y", visible=False)
    for index, value in enumerate(plot_df["importance"]):
        ax.text(value + 0.003, index, f"{value:.3f}", va="center", fontsize=8)
    fig.text(
        0.01,
        0.01,
        "Note: Higher values indicate greater contribution to the Random Forest split decisions.",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#555555",
    )
    save_figure(fig, "feature_importance")


def save_permutation_importance(model, x_test, y_test):
    permutation_result = permutation_importance(
        model,
        x_test,
        y_test,
        n_repeats=30,
        random_state=RANDOM_STATE,
        scoring="f1",
    )
    feature_names = x_test.columns

    importance_df = (
        pd.DataFrame(
            {
                "feature": feature_names,
                "feature_label": [clean_feature_name(feature) for feature in feature_names],
                "importance": permutation_result.importances_mean,
                "importance_std": permutation_result.importances_std,
            }
        )
        .sort_values("importance", ascending=False)
    )
    importance_df.to_csv(RESULTS_DIR / "permutation_importance.csv", index=False)
    plot_df = importance_df.sort_values("importance", ascending=True)

    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    ax.barh(
        plot_df["feature_label"],
        plot_df["importance"],
        xerr=plot_df["importance_std"],
        color="#4C78A8",
        edgecolor="#222222",
        linewidth=0.4,
        capsize=3,
    )
    ax.axvline(0, color="#333333", linewidth=0.9)
    ax.set_title("Permutation Feature Importance")
    ax.set_xlabel("Mean decrease in F1-score after permutation")
    ax.set_ylabel("")
    ax.grid(axis="x", alpha=0.45)
    ax.grid(axis="y", visible=False)
    fig.text(
        0.01,
        0.01,
        "Note: Error bars show standard deviation across 30 random permutations.",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#555555",
    )
    save_figure(fig, "permutation_importance")


def save_metrics_comparison(metrics_df):
    plot_df = metrics_df.melt(
        id_vars="model",
        value_vars=["accuracy", "precision", "recall", "f1", "roc_auc"],
        var_name="metric",
        value_name="score",
    )
    metric_labels = {
        "accuracy": "Accuracy",
        "precision": "Precision",
        "recall": "Recall",
        "f1": "F1-score",
        "roc_auc": "ROC-AUC",
    }
    plot_df["metric"] = plot_df["metric"].map(metric_labels)

    fig, ax = plt.subplots(figsize=(8.2, 5.0))
    sns.barplot(
        data=plot_df,
        x="metric",
        y="score",
        hue="model",
        palette=["#4C78A8", "#D55E00"],
        edgecolor="#222222",
        linewidth=0.4,
        ax=ax,
    )
    ax.set_title("Model Performance on the Held-Out Test Set")
    ax.set_xlabel("")
    ax.set_ylabel("Score")
    ax.set_ylim(0, 1.05)
    ax.legend(title="Model", frameon=True, loc="lower right")
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", padding=2, fontsize=8)
    ax.grid(axis="y", alpha=0.45)
    ax.grid(axis="x", visible=False)
    save_figure(fig, "model_metrics_comparison")


def save_eda_figures(country_df, high_risk_threshold):
    risk_order = ["Low/Medium Risk", "High Risk"]
    continent_order = (
        country_df.groupby("continent")["mortality_risk"]
        .mean()
        .sort_values(ascending=False)
        .index
    )
    counts = pd.crosstab(country_df["continent"], country_df["mortality_risk_label"])
    counts = counts.reindex(index=continent_order, columns=risk_order).fillna(0)
    shares = counts.div(counts.sum(axis=1), axis=0)

    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    bottom = np.zeros(len(shares))
    for label in risk_order:
        values = shares[label].to_numpy()
        ax.bar(
            shares.index,
            values,
            bottom=bottom,
            label=label,
            color=RISK_PALETTE[label],
            edgecolor="white",
            linewidth=0.6,
        )
        bottom += values

    for idx, continent in enumerate(shares.index):
        total = int(counts.loc[continent].sum())
        high_share = shares.loc[continent, "High Risk"]
        ax.text(idx, 1.025, f"n={total}", ha="center", va="bottom", fontsize=8, color="#444444")
        ax.text(
            idx,
            max(0.03, shares.loc[continent, "Low/Medium Risk"] + high_share / 2),
            f"{high_share:.0%}",
            ha="center",
            va="center",
            fontsize=8,
            color="white" if high_share > 0.16 else "#333333",
            fontweight="bold",
        )

    ax.set_title("Share of Countries Classified as High Mortality Risk by Continent")
    ax.set_xlabel("Continent")
    ax.set_ylabel("Share of countries")
    ax.set_ylim(0, 1.12)
    ax.set_yticks(np.linspace(0, 1, 6))
    ax.set_yticklabels([f"{value:.0%}" for value in np.linspace(0, 1, 6)])
    ax.tick_params(axis="x", rotation=30)
    ax.legend(title="Risk group", frameon=True, loc="upper right")
    ax.grid(axis="y", alpha=0.45)
    ax.grid(axis="x", visible=False)
    save_figure(fig, "risk_distribution_by_continent")

    scatter_df = country_df.dropna(
        subset=[
            "people_fully_vaccinated_per_hundred",
            "total_deaths_per_million",
            "mortality_risk_label",
        ]
    )
    fig, ax = plt.subplots(figsize=(8.4, 5.6))
    sns.scatterplot(
        data=scatter_df,
        x="people_fully_vaccinated_per_hundred",
        y="total_deaths_per_million",
        hue="mortality_risk_label",
        hue_order=risk_order,
        ax=ax,
        palette=RISK_PALETTE,
        s=58,
        alpha=0.82,
        edgecolor="#222222",
        linewidth=0.35,
    )
    x_values = scatter_df["people_fully_vaccinated_per_hundred"].to_numpy()
    y_values = scatter_df["total_deaths_per_million"].to_numpy()
    slope, intercept = np.polyfit(x_values, y_values, 1)
    line_x = np.linspace(np.nanmin(x_values), np.nanmax(x_values), 100)
    ax.plot(
        line_x,
        slope * line_x + intercept,
        color="#333333",
        linewidth=1.6,
        label="Linear trend",
    )
    ax.axhline(
        high_risk_threshold,
        color="#333333",
        linestyle="--",
        linewidth=1.2,
        label=f"High-risk threshold ({high_risk_threshold:.0f})",
    )
    ax.set_title("Vaccination Coverage and COVID-19 Mortality Risk")
    ax.set_xlabel("Fully vaccinated people per hundred")
    ax.set_ylabel("Total deaths per million")
    ax.legend(title="", frameon=True, loc="upper left")
    ax.grid(True, alpha=0.45)
    fig.text(
        0.01,
        0.01,
        "Note: Countries above the dashed line are labeled as high mortality risk.",
        ha="left",
        va="bottom",
        fontsize=8,
        color="#555555",
    )
    save_figure(fig, "vaccination_vs_mortality_risk")


def main():
    country_df, high_risk_threshold = build_country_level_dataset(DATA_PATH)
    country_df.to_csv(RESULTS_DIR / "country_mortality_risk_dataset.csv", index=False)

    numeric_features = [
        "people_fully_vaccinated_per_hundred",
        "gdp_per_capita",
        "median_age",
        "life_expectancy",
        "population_density",
        "diabetes_prevalence",
        "hospital_beds_per_thousand",
    ]
    categorical_features = ["continent"]

    x = country_df[numeric_features + categorical_features]
    y = country_df["mortality_risk"]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.25,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    models = make_models(numeric_features, categorical_features)

    metrics_list = []
    reports = []
    fitted_models = {}

    for name, model in models.items():
        metrics, report = evaluate_model(name, model, x_train, x_test, y_train, y_test)
        metrics_list.append(metrics)
        reports.append(f"\n{name}\n{'=' * len(name)}\n{report}")
        fitted_models[name] = model

    metrics_df = pd.DataFrame(metrics_list)
    metrics_df.to_csv(RESULTS_DIR / "model_metrics.csv", index=False)
    save_metrics_comparison(metrics_df)

    best_model_name = metrics_df.sort_values("f1", ascending=False).iloc[0]["model"]
    best_model = fitted_models[best_model_name]

    save_confusion_matrix(best_model, x_test, y_test)
    save_roc_curve(best_model, x_test, y_test)

    save_feature_importance(fitted_models["Random Forest"])
    save_permutation_importance(best_model, x_test, y_test)

    save_eda_figures(country_df, high_risk_threshold)

    summary = [
        "COVID-19 high mortality risk classification",
        "",
        f"Input file: {DATA_PATH}",
        f"Country-level rows used: {len(country_df)}",
        f"High-risk threshold: {high_risk_threshold:.2f} deaths per million",
        f"High-risk countries: {int(y.sum())}",
        f"Low/medium-risk countries: {int((y == 0).sum())}",
        f"Best model by F1 score: {best_model_name}",
        "",
        "Model metrics:",
        metrics_df.to_string(index=False),
        "",
        "Classification reports:",
        "\n".join(reports),
    ]

    (RESULTS_DIR / "model_summary.txt").write_text("\n".join(summary), encoding="utf-8")

    print("\n".join(summary[:12]))
    print(f"\nOutputs saved to: {OUTPUT_DIR}")
    print(f"Tables and summaries saved to: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
