import fs from "node:fs/promises";
import path from "node:path";
import {
  Presentation,
  PresentationFile,
  row,
  column,
  grid,
  layers,
  panel,
  text,
  image,
  shape,
  rule,
  fill,
  fixed,
  hug,
  wrap,
  grow,
  fr,
  auto,
} from "@oai/artifact-tool";

const W = 1920;
const H = 1080;
const outDir = "output";
const scratchDir = "scratch";
const previewDir = path.join(scratchDir, "previews");
const pptxPreviewDir = path.join(scratchDir, "pptx-previews");
const layoutDir = path.join(scratchDir, "layouts");

const colors = {
  bg: "#F6FAF9",
  bg2: "#EAF4F1",
  ink: "#102326",
  muted: "#5D7373",
  teal: "#0F766E",
  cyan: "#2CA6A4",
  coral: "#E45C69",
  amber: "#F1B44C",
  navy: "#123047",
  pale: "#DDEEEA",
  white: "#FFFFFF",
  line: "#BCD2CE",
};

const font = {
  display: "Microsoft YaHei",
  body: "Microsoft YaHei",
  mono: "Consolas",
};

const img = (relativePath) => path.resolve(relativePath);

const assetPaths = {
  cases: img("Insights/COVID-19_time/daily_new_cases_trend.png"),
  deaths: img("Insights/COVID-19_time/daily_new_deaths_trend.png"),
  topCountries: img("Insights/Countries_compare/top_affected_countries.png"),
  continents: img("Insights/Countries_compare/continent_comparison.png"),
  vaccContinent: img("Insights/Countries_vaccinationCoverage/vaccination_coverage_by_continent.png"),
  gdpVacc: img("Insights/Countries_vaccinationCoverage/gdp_vaccination_coverage.png"),
  populationSpread: img("Insights/Population&Spread/log_plot_final.png"),
  vaccMortality: img("Insights/Vaccination_mortality/vaccination_vs_mortality_regression.png"),
  metrics: img("ML_mortality_risk/outputs/model_metrics_comparison.png"),
  confusion: img("ML_mortality_risk/outputs/confusion_matrix.png"),
  featureImportance: img("ML_mortality_risk/outputs/feature_importance.png"),
};

let assets = {};

async function loadAssets() {
  const loaded = {};
  for (const [key, filePath] of Object.entries(assetPaths)) {
    loaded[key] = {
      data: await fs.readFile(filePath),
      contentType: "image/png",
      label: path.relative(process.cwd(), filePath).replaceAll("\\", "/"),
    };
  }
  return loaded;
}

function titleStyle(size = 58, color = colors.ink) {
  return { fontFamily: font.display, fontSize: size, bold: true, color, lineSpacingMultiple: 0.95 };
}

function bodyStyle(size = 27, color = colors.ink) {
  return { fontFamily: font.body, fontSize: size, color, lineSpacingMultiple: 1.18 };
}

function labelStyle(size = 18, color = colors.teal) {
  return { fontFamily: font.body, fontSize: size, bold: true, color, letterSpacing: 0 };
}

function monoStyle(size = 20, color = colors.muted) {
  return { fontFamily: font.mono, fontSize: size, color };
}

function chip(value, fillColor = colors.pale, textColor = colors.teal) {
  return panel(
    {
      name: `chip-${value.replaceAll(" ", "-").slice(0, 24)}`,
      width: hug,
      height: hug,
      padding: { x: 18, y: 8 },
      fill: fillColor,
      borderRadius: 20,
    },
    text(value, { width: hug, height: hug, style: labelStyle(16, textColor) }),
  );
}

function footer(slideNo, section = "COVID-19 Global Analysis Dashboard") {
  return row(
    {
      name: `footer-${slideNo}`,
      width: fill,
      height: hug,
      align: "center",
      justify: "between",
    },
    [
      text(section, { name: `footer-label-${slideNo}`, width: wrap(1000), height: hug, style: labelStyle(13, colors.muted) }),
      text(String(slideNo).padStart(2, "0"), { name: `footer-number-${slideNo}`, width: hug, height: hug, style: labelStyle(15, colors.teal) }),
    ],
  );
}

function slideShell(slide, slideNo, title, subtitle, bodyChildren, opts = {}) {
  const bg = opts.dark ? colors.navy : colors.bg;
  const titleColor = opts.dark ? colors.white : colors.ink;
  const subtitleColor = opts.dark ? "#C9E2DD" : colors.muted;
  slide.compose(
    layers({ name: `slide-${slideNo}-shell`, width: fill, height: fill }, [
      shape({ name: `slide-${slideNo}-background`, width: fill, height: fill, fill: bg }),
      grid(
        {
          name: `slide-${slideNo}-root`,
          width: fill,
          height: fill,
          columns: [fr(1)],
          rows: [auto, fr(1), auto],
          padding: { x: 86, y: 58 },
          rowGap: 30,
        },
        [
          column({ name: `slide-${slideNo}-title-stack`, width: fill, height: hug, gap: 12 }, [
            row({ name: `slide-${slideNo}-eyebrow-row`, width: fill, height: hug, align: "center", justify: "between" }, [
              chip(opts.section ?? `0${slideNo}`, opts.dark ? "#1E4F55" : colors.pale, opts.dark ? "#DDF7F3" : colors.teal),
              text(opts.kicker ?? "Group 06 · Data Programming Workshop", {
                name: `slide-${slideNo}-kicker`,
                width: hug,
                height: hug,
                style: labelStyle(14, opts.dark ? "#9FD4CD" : colors.muted),
              }),
            ]),
            text(title, {
              name: `slide-${slideNo}-title`,
              width: wrap(1500),
              height: hug,
              style: titleStyle(opts.titleSize ?? 53, titleColor),
            }),
            subtitle
              ? text(subtitle, {
                  name: `slide-${slideNo}-subtitle`,
                  width: wrap(1420),
                  height: hug,
                  style: bodyStyle(24, subtitleColor),
                })
              : rule({ name: `slide-${slideNo}-title-rule`, width: fixed(260), stroke: opts.dark ? colors.cyan : colors.teal, weight: 5 }),
          ]),
          column({ name: `slide-${slideNo}-body`, width: fill, height: fill, gap: 24 }, bodyChildren),
          footer(slideNo, opts.footer ?? "COVID-19 Global Analysis Dashboard"),
        ],
      ),
    ]),
    { frame: { left: 0, top: 0, width: W, height: H }, baseUnit: 8 },
  );
}

function imagePanel(name, title, filePath, caption = "", options = {}) {
  return column(
    { name: `${name}-wrap`, width: fill, height: fill, gap: 10 },
    [
      row({ name: `${name}-caption-row`, width: fill, height: hug, align: "center", justify: "between" }, [
        text(title, { name: `${name}-title`, width: wrap(820), height: hug, style: labelStyle(20, colors.ink) }),
        caption ? text(caption, { name: `${name}-caption`, width: hug, height: hug, style: labelStyle(13, colors.muted) }) : text("", { width: fixed(1), height: hug, style: labelStyle(1, colors.muted) }),
      ]),
      panel(
        {
          name: `${name}-image-frame`,
          width: fill,
          height: fill,
          fill: colors.white,
          line: { color: colors.line, width: 1 },
          borderRadius: 8,
          padding: options.padding ?? 18,
        },
        image({ name, blob: filePath.data, contentType: filePath.contentType, width: fill, height: fill, fit: options.fit ?? "contain", alt: title, borderRadius: 5 }),
      ),
    ],
  );
}

function placeholder(name, title, detail, accent = colors.teal) {
  return panel(
    {
      name: `${name}-placeholder`,
      width: fill,
      height: fill,
      fill: "#FFFFFFCC",
      line: { color: accent, width: 2, dash: "dash" },
      borderRadius: 8,
      padding: { x: 28, y: 26 },
    },
    column({ name: `${name}-placeholder-stack`, width: fill, height: fill, gap: 16, justify: "center" }, [
      text(title, { name: `${name}-placeholder-title`, width: fill, height: hug, style: titleStyle(30, accent) }),
      text(detail, { name: `${name}-placeholder-detail`, width: wrap(680), height: hug, style: bodyStyle(22, colors.muted) }),
    ]),
  );
}

function noteList(name, items, accent = colors.teal) {
  return column(
    { name, width: fill, height: hug, gap: 13 },
    items.map((item, index) =>
      row({ name: `${name}-row-${index + 1}`, width: fill, height: hug, gap: 14, align: "start" }, [
        shape({ name: `${name}-dot-${index + 1}`, width: fixed(13), height: fixed(13), fill: accent, borderRadius: 99 }),
        text(item, { name: `${name}-text-${index + 1}`, width: fill, height: hug, style: bodyStyle(23, colors.ink) }),
      ]),
    ),
  );
}

function miniMetric(label, value, hint, color = colors.teal) {
  return column({ name: `metric-${label}`, width: fill, height: hug, gap: 6 }, [
    text(value, { name: `metric-${label}-value`, width: fill, height: hug, style: titleStyle(44, color) }),
    text(label, { name: `metric-${label}-label`, width: fill, height: hug, style: labelStyle(16, colors.ink) }),
    text(hint, { name: `metric-${label}-hint`, width: wrap(310), height: hug, style: bodyStyle(17, colors.muted) }),
  ]);
}

function addCover(presentation) {
  const slide = presentation.slides.add();
  slide.compose(
    layers({ name: "cover-shell", width: fill, height: fill }, [
      shape({ name: "cover-bg", width: fill, height: fill, fill: colors.navy }),
      grid(
        {
          name: "cover-root",
          width: fill,
          height: fill,
          columns: [fr(1.15), fr(0.85)],
          padding: { x: 96, y: 72 },
          columnGap: 58,
        },
        [
          column({ name: "cover-left", width: fill, height: fill, gap: 28, justify: "center" }, [
            row({ name: "cover-wordmark-row", width: fill, height: hug, gap: 0, align: "end" }, [
              text("COVID", { name: "cover-wordmark-covid", width: hug, height: hug, style: titleStyle(118, colors.white) }),
              text("-19", { name: "cover-wordmark-19", width: hug, height: hug, style: titleStyle(118, colors.white) }),
            ]),
            text("Global Analysis Dashboard", { name: "cover-title", width: wrap(860), height: hug, style: titleStyle(54, "#D6F2ED") }),
            rule({ name: "cover-rule", width: fixed(360), stroke: colors.coral, weight: 7 }),
            text("Data cleaning · insights · mortality risk modeling · Streamlit dashboard", {
              name: "cover-subtitle",
              width: wrap(860),
              height: hug,
              style: bodyStyle(28, "#BADAD4"),
            }),
            text("Group 06 / 成员姓名：____________________________", {
              name: "cover-members",
              width: wrap(900),
              height: hug,
              style: bodyStyle(24, "#E8FAF6"),
            }),
          ]),
          column({ name: "cover-right", width: fill, height: fill, gap: 18, justify: "center" }, [
            row({ name: "cover-strip-1", width: fill, height: fixed(74), gap: 14 }, [
              shape({ width: fixed(180), height: fill, fill: colors.coral, borderRadius: 8 }),
              shape({ width: fixed(112), height: fill, fill: "#2CA6A4", borderRadius: 8 }),
              shape({ width: fixed(240), height: fill, fill: "#D7EFEA", borderRadius: 8 }),
            ]),
            row({ name: "cover-strip-2", width: fill, height: fixed(74), gap: 14 }, [
              shape({ width: fixed(128), height: fill, fill: "#D7EFEA", borderRadius: 8 }),
              shape({ width: fixed(260), height: fill, fill: colors.amber, borderRadius: 8 }),
              shape({ width: fixed(146), height: fill, fill: colors.cyan, borderRadius: 8 }),
            ]),
            row({ name: "cover-strip-3", width: fill, height: fixed(74), gap: 14 }, [
              shape({ width: fixed(286), height: fill, fill: "#1E4F55", borderRadius: 8 }),
              shape({ width: fixed(128), height: fill, fill: colors.coral, borderRadius: 8 }),
              shape({ width: fixed(112), height: fill, fill: "#D7EFEA", borderRadius: 8 }),
            ]),
            panel(
              {
                name: "cover-legend",
                width: fill,
                height: hug,
                fill: "#0B242B",
                line: { color: "#2A5960", width: 1 },
                borderRadius: 8,
                padding: { x: 26, y: 22 },
              },
              column({ width: fill, height: hug, gap: 10 }, [
                text("Template sections", { name: "cover-legend-title", width: fill, height: hug, style: labelStyle(18, "#9FD4CD") }),
                text("Background / Cleaning / Insights / ML / Demo / Conclusion", {
                  name: "cover-legend-body",
                  width: wrap(620),
                  height: hug,
                  style: bodyStyle(24, colors.white),
                }),
              ]),
            ),
          ]),
        ],
      ),
    ]),
    { frame: { left: 0, top: 0, width: W, height: H }, baseUnit: 8 },
  );
}

function addBackgroundSlide(presentation) {
  const slide = presentation.slides.add();
  slideShell(
    slide,
    2,
    "Project Background",
    "Motivation & questions: explain why this dashboard matters, and what questions your analysis answers.",
    [
      grid(
        { name: "background-grid", width: fill, height: fill, columns: [fr(1.05), fr(0.95)], columnGap: 42 },
        [
          column({ name: "background-questions", width: fill, height: fill, gap: 24, justify: "center" }, [
            text("Core Questions", { name: "background-core-title", width: fill, height: hug, style: titleStyle(38, colors.teal) }),
            noteList("background-question-list", [
              "疫情如何在国家/地区之间随时间变化？",
              "疫苗接种覆盖率是否与死亡率、风险水平相关？",
              "能否利用人口、经济和疫情指标预测死亡风险？",
            ], colors.coral),
          ]),
          panel(
            {
              name: "background-talking-points",
              width: fill,
              height: fill,
              fill: colors.white,
              line: { color: colors.line, width: 1 },
              borderRadius: 8,
              padding: { x: 34, y: 30 },
            },
            column({ width: fill, height: fill, gap: 20, justify: "center" }, [
              text("Speaker prompt / 讲稿提示", { width: fill, height: hug, style: labelStyle(20, colors.teal) }),
              text("用 2-3 句话说明：COVID-19 数据量大、国家差异明显，因此需要一个从清洗、洞察到模型预测的完整分析流程。", {
                width: fill,
                height: hug,
                style: bodyStyle(25, colors.ink),
              }),
              rule({ width: fill, stroke: colors.line, weight: 1 }),
              text("Replace this block with your final motivation after analysis is complete.", {
                width: wrap(680),
                height: hug,
                style: bodyStyle(20, colors.muted),
              }),
            ]),
          ),
        ],
      ),
    ],
    { section: "02 / Background" },
  );
}

function addSystemSlide(presentation) {
  const slide = presentation.slides.add();
  slideShell(
    slide,
    3,
    "System Overview",
    "A compact pipeline from raw COVID data to explainable dashboard and mortality-risk prediction.",
    [
      column({ name: "system-body", width: fill, height: fill, gap: 30, justify: "center" }, [
        row({ name: "system-pipeline", width: fill, height: hug, gap: 22, align: "center" }, [
          pipelineStep("01", "Data Cleaning", "missing values / country split", colors.teal),
          arrowStep(),
          pipelineStep("02", "Insights", "time, country, vaccination", colors.cyan),
          arrowStep(),
          pipelineStep("03", "ML Mortality Risk", "features / target / comparison", colors.coral),
          arrowStep(),
          pipelineStep("04", "Streamlit Dashboard", "interactive pages / demo", colors.amber),
        ]),
        grid({ name: "system-notes", width: fill, height: hug, columns: [fr(1), fr(1), fr(1)], columnGap: 22 }, [
          systemNote("DataCleaning", "compact_clean.csv + country-level CSV files"),
          systemNote("Insights", "trend plots, coverage analysis, comparison visuals"),
          systemNote("ML_mortality_risk", "model metrics, confusion matrix, feature importance"),
        ]),
      ]),
    ],
    { section: "03 / System" },
  );
}

function pipelineStep(num, label, detail, color) {
  return panel(
    { name: `pipeline-${num}`, width: grow(1), height: fixed(188), fill: colors.white, line: { color, width: 2 }, borderRadius: 8, padding: { x: 24, y: 24 } },
    column({ width: fill, height: fill, gap: 10, justify: "center" }, [
      text(num, { width: fill, height: hug, style: labelStyle(17, color) }),
      text(label, { width: fill, height: hug, style: titleStyle(27, colors.ink) }),
      text(detail, { width: fill, height: hug, style: bodyStyle(18, colors.muted) }),
    ]),
  );
}

function arrowStep() {
  return text("→", { name: `arrow-${Math.random()}`, width: hug, height: hug, style: titleStyle(36, colors.muted) });
}

function systemNote(title, detail) {
  return column({ name: `system-note-${title}`, width: fill, height: hug, gap: 8 }, [
    text(title, { width: fill, height: hug, style: monoStyle(19, colors.teal) }),
    text(detail, { width: fill, height: hug, style: bodyStyle(20, colors.ink) }),
  ]);
}

function addCleaningSlide(presentation) {
  const slide = presentation.slides.add();
  slideShell(
    slide,
    4,
    "Data & Cleaning",
    "Show how raw data becomes compact, analysis-ready country-level datasets.",
    [
      grid({ name: "cleaning-grid", width: fill, height: fill, columns: [fr(0.85), fr(1.15)], columnGap: 36 }, [
        panel(
          { name: "cleaning-output", width: fill, height: fill, fill: colors.white, line: { color: colors.line, width: 1 }, borderRadius: 8, padding: { x: 30, y: 28 } },
          column({ width: fill, height: fill, gap: 20, justify: "center" }, [
            text("Cleaning Checklist", { width: fill, height: hug, style: titleStyle(34, colors.teal) }),
            noteList("cleaning-list", [
              "选择主要字段：cases, deaths, vaccinations, population, GDP 等",
              "处理缺失值与异常值，统一国家/地区命名",
              "按国家拆分并生成 country/*.csv",
              "输出 compact_clean.csv 供 Insights 与 ML 复用",
            ], colors.teal),
          ]),
        ),
        placeholder("cleaning-table", "Data schema / cleaning summary", "放置 compact_clean.csv 字段表、缺失值处理前后对比、或清洗流程截图。", colors.coral),
      ]),
    ],
    { section: "04 / Cleaning" },
  );
}

function addTrendSlide(presentation) {
  const slide = presentation.slides.add();
  slideShell(
    slide,
    5,
    "Time Trend Analysis",
    "Use daily cases and deaths trends to explain how the pandemic evolved over time.",
    [
      grid({ name: "trend-grid", width: fill, height: fill, columns: [fr(1), fr(1)], columnGap: 26 }, [
        imagePanel("daily-cases", "Daily new cases trend", assets.cases, "Insights/COVID-19_time", { fit: "contain" }),
        imagePanel("daily-deaths", "Daily new deaths trend", assets.deaths, "Insights/COVID-19_time", { fit: "contain" }),
      ]),
    ],
    { section: "05 / Trend" },
  );
}

function addComparisonSlide(presentation) {
  const slide = presentation.slides.add();
  slideShell(
    slide,
    6,
    "Global and Country Comparison",
    "Compare highly affected countries and continent-level differences, then summarize the strongest geographic signal.",
    [
      grid({ name: "comparison-grid", width: fill, height: fill, columns: [fr(1.1), fr(0.9)], rows: [fr(1), fixed(160)], columnGap: 28, rowGap: 20 }, [
        imagePanel("top-countries", "Top affected countries", assets.topCountries, "top_affected_countries.png", { fit: "contain" }),
        imagePanel("continent-comparison", "Continent comparison", assets.continents, "continent_comparison.png", { fit: "contain" }),
        panel(
          { name: "map-note", width: fill, height: fill, columnSpan: 2, fill: colors.bg2, line: { color: colors.line, width: 1 }, borderRadius: 8, padding: { x: 26, y: 20 } },
          row({ width: fill, height: fill, gap: 22, align: "center" }, [
            text("Optional map", { width: wrap(230), height: hug, style: titleStyle(26, colors.teal) }),
            text("可加入 covid_world_map.html 的截图，说明全球空间分布。保留一句主要发现，避免把地图页讲成列表页。", {
              width: fill,
              height: hug,
              style: bodyStyle(22, colors.ink),
            }),
          ]),
        ),
      ]),
    ],
    { section: "06 / Compare" },
  );
}

function addVaccinationSlide(presentation) {
  const slide = presentation.slides.add();
  slideShell(
    slide,
    7,
    "Vaccination Coverage",
    "Explain vaccination coverage gaps across countries or continents.",
    [
      grid({ name: "vacc-grid", width: fill, height: fill, columns: [fr(1.15), fr(0.85)], columnGap: 32 }, [
        imagePanel("vacc-continent", "Vaccination coverage by continent", assets.vaccContinent, "vaccination_coverage_by_continent.png", { fit: "contain" }),
        column({ name: "vacc-talk", width: fill, height: fill, gap: 22, justify: "center" }, [
          text("Talk track", { width: fill, height: hug, style: titleStyle(34, colors.teal) }),
          noteList("vacc-notes", [
            "指出不同洲或国家的覆盖率差异。",
            "解释可能原因：经济水平、可及性、政策与时间滞后。",
            "连接到下一页：覆盖率是否也与 GDP、人口或死亡率有关？",
          ], colors.coral),
        ]),
      ]),
    ],
    { section: "07 / Vaccination" },
  );
}

function addGdpPopulationSlide(presentation) {
  const slide = presentation.slides.add();
  slideShell(
    slide,
    8,
    "GDP / Population / Spread Insight",
    "Connect economic level, population scale, and spread indicators before moving into mortality-risk modeling.",
    [
      grid({ name: "gdp-grid", width: fill, height: fill, columns: [fr(1), fr(1)], columnGap: 26 }, [
        imagePanel("gdp-vaccination", "GDP vs vaccination coverage", assets.gdpVacc, "gdp_vaccination_coverage.png", { fit: "contain" }),
        imagePanel("population-spread", "Population vs spread", assets.populationSpread, "log_plot_final.png", { fit: "contain" }),
      ]),
    ],
    { section: "08 / GDP & Spread" },
  );
}

function addVaccMortalitySlide(presentation) {
  const slide = presentation.slides.add();
  slideShell(
    slide,
    9,
    "Vaccination vs Mortality",
    "Use the regression visual to discuss whether vaccination coverage appears negatively associated with mortality.",
    [
      grid({ name: "vacc-mort-grid", width: fill, height: fill, columns: [fr(1.18), fr(0.82)], columnGap: 34 }, [
        imagePanel("vacc-mortality", "Vaccination vs mortality regression", assets.vaccMortality, "vaccination_vs_mortality_regression.png", { fit: "contain" }),
        panel(
          { name: "vacc-mort-interpretation", width: fill, height: fill, fill: colors.white, line: { color: colors.line, width: 1 }, borderRadius: 8, padding: { x: 30, y: 30 } },
          column({ width: fill, height: fill, gap: 22, justify: "center" }, [
            text("Interpretation", { width: fill, height: hug, style: titleStyle(34, colors.teal) }),
            noteList("vacc-mort-list", [
              "先描述趋势方向，再说明相关不等于因果。",
              "若有离群国家，点名并解释可能原因。",
              "把结论连到 ML：模型将综合更多变量判断死亡风险。",
            ], colors.teal),
          ]),
        ),
      ]),
    ],
    { section: "09 / Mortality" },
  );
}

function addMlModelSlide(presentation) {
  const slide = presentation.slides.add();
  slideShell(
    slide,
    10,
    "ML Model",
    "Frame mortality-risk classification: inputs, target variable, model candidates, and evaluation logic.",
    [
      grid({ name: "ml-grid", width: fill, height: fill, columns: [fr(1), fr(1), fr(1)], columnGap: 24 }, [
        mlBlock("Inputs", ["vaccination rate", "GDP / population", "cases & deaths", "continent / country features"], colors.teal),
        mlBlock("Target", ["mortality risk class", "low / medium / high", "derived from death-rate threshold"], colors.coral),
        mlBlock("Compare", ["Logistic Regression", "Random Forest", "Gradient Boosting", "metrics + confusion matrix"], colors.amber),
      ]),
    ],
    { section: "10 / ML Model" },
  );
}

function mlBlock(title, items, color) {
  return panel(
    { name: `ml-${title}`, width: fill, height: fill, fill: colors.white, line: { color, width: 2 }, borderRadius: 8, padding: { x: 28, y: 28 } },
    column({ width: fill, height: fill, gap: 20, justify: "center" }, [
      text(title, { width: fill, height: hug, style: titleStyle(36, color) }),
      noteList(`ml-${title}-items`, items, color),
    ]),
  );
}

function addModelResultSlide(presentation) {
  const slide = presentation.slides.add();
  slideShell(
    slide,
    11,
    "Model Result",
    "Show which model performs best and which features most strongly explain mortality-risk classification.",
    [
      grid({ name: "model-result-grid", width: fill, height: fill, columns: [fr(1), fr(0.82)], rows: [fr(1), fr(1)], columnGap: 24, rowGap: 20 }, [
        imagePanel("model-metrics", "Model metrics comparison", assets.metrics, "model_metrics_comparison.png", { fit: "contain" }),
        imagePanel("confusion-matrix", "Confusion matrix", assets.confusion, "confusion_matrix.png", { fit: "contain" }),
        imagePanel("feature-importance", "Feature importance", assets.featureImportance, "feature_importance.png", { fit: "contain" }),
        panel(
          { name: "model-result-summary", width: fill, height: fill, fill: colors.bg2, line: { color: colors.line, width: 1 }, borderRadius: 8, padding: { x: 24, y: 24 } },
          column({ width: fill, height: fill, gap: 16, justify: "center" }, [
            text("Summary line", { width: fill, height: hug, style: titleStyle(28, colors.teal) }),
            text("写明：哪个模型最好、原因是什么、最重要特征是什么。", { width: fill, height: hug, style: bodyStyle(21, colors.ink) }),
          ]),
        ),
      ]),
    ],
    { section: "11 / Results", titleSize: 49 },
  );
}

function addDashboardDemoSlide(presentation) {
  const slide = presentation.slides.add();
  slideShell(
    slide,
    12,
    "Dashboard Demo Video",
    "Reserve 30-45 seconds to open the Streamlit dashboard, switch pages, and show charts plus model outputs.",
    [
      grid({ name: "demo-grid", width: fill, height: fill, columns: [fr(1.25), fr(0.75)], columnGap: 34 }, [
        placeholder("demo-video", "Video placeholder", "插入 30-45 秒 dashboard 演示视频或放置 dashboard.py 运行截图。", colors.coral),
        column({ name: "demo-steps", width: fill, height: fill, gap: 20, justify: "center" }, [
          text("Demo route", { width: fill, height: hug, style: titleStyle(34, colors.teal) }),
          noteList("demo-step-list", [
            "Home / overview: show project scope.",
            "Trend and comparison pages: switch 2-3 visuals.",
            "Vaccination and ML pages: show model result.",
            "End with a clear dashboard takeaway.",
          ], colors.teal),
        ]),
      ]),
    ],
    { section: "12 / Demo" },
  );
}

function addConclusionSlide(presentation) {
  const slide = presentation.slides.add();
  slideShell(
    slide,
    13,
    "Conclusion & Limitations",
    "Close with three findings, then be honest about data quality, time lag, and model improvement.",
    [
      grid({ name: "conclusion-grid", width: fill, height: fill, columns: [fr(1.05), fr(0.95)], columnGap: 36 }, [
        column({ name: "conclusion-left", width: fill, height: fill, gap: 28, justify: "center" }, [
          text("Three takeaways", { width: fill, height: hug, style: titleStyle(36, colors.teal) }),
          noteList("conclusion-takeaways", [
            "全球差异明显：疫情影响在国家与洲之间并不均衡。",
            "疫苗、经济与人口因素与死亡风险存在关联。",
            "Dashboard 能把清洗、洞察与模型结果整合成可探索工具。",
          ], colors.coral),
        ]),
        panel(
          { name: "future-work", width: fill, height: fill, fill: colors.white, line: { color: colors.line, width: 1 }, borderRadius: 8, padding: { x: 34, y: 30 } },
          column({ width: fill, height: fill, gap: 24, justify: "center" }, [
            text("Limitations / Future Work", { width: fill, height: hug, style: titleStyle(33, colors.navy) }),
            noteList("limitation-list", [
              "数据质量限制与国家统计口径差异。",
              "时间滞后会影响趋势解释与模型输入。",
              "可加入更多变量并继续优化模型。",
            ], colors.teal),
            rule({ width: fill, stroke: colors.line, weight: 1 }),
            text("Q&A", { width: fill, height: hug, style: titleStyle(42, colors.coral) }),
          ]),
        ),
      ]),
    ],
    { section: "13 / Close" },
  );
}

async function saveSlideExports(presentation, directory) {
  await fs.mkdir(directory, { recursive: true });
  for (const [index, slide] of presentation.slides.items.entries()) {
    const number = String(index + 1).padStart(2, "0");
    const png = await slide.export({ format: "png" });
    const bytes = Buffer.from(await png.arrayBuffer());
    await fs.writeFile(path.join(directory, `slide-${number}.png`), bytes);
  }
}

async function saveLayoutExports(presentation) {
  await fs.mkdir(layoutDir, { recursive: true });
  for (const slide of presentation.slides.items) {
    const number = String(slide.index + 1).padStart(2, "0");
    const layout = await slide.export({ format: "layout" });
    await fs.writeFile(path.join(layoutDir, `slide-${number}.layout.json`), JSON.stringify(layout, null, 2), "utf8");
  }
}

async function build() {
  await fs.mkdir(outDir, { recursive: true });
  await fs.mkdir(scratchDir, { recursive: true });
  assets = await loadAssets();

  const presentation = Presentation.create({
    slideSize: { width: W, height: H },
  });

  addCover(presentation);
  addBackgroundSlide(presentation);
  addSystemSlide(presentation);
  addCleaningSlide(presentation);
  addTrendSlide(presentation);
  addComparisonSlide(presentation);
  addVaccinationSlide(presentation);
  addGdpPopulationSlide(presentation);
  addVaccMortalitySlide(presentation);
  addMlModelSlide(presentation);
  addModelResultSlide(presentation);
  addDashboardDemoSlide(presentation);
  addConclusionSlide(presentation);

  const pptx = await PresentationFile.exportPptx(presentation);
  const deckPath = path.join(outDir, "COVID19_Global_Analysis_Dashboard_Template.pptx");
  await pptx.save(deckPath);
  await pptx.save(path.join(outDir, "output.pptx"));

  await saveSlideExports(presentation, previewDir);
  await saveLayoutExports(presentation);

  const savedBytes = await fs.readFile(deckPath);
  const imported = await PresentationFile.importPptx(savedBytes);
  await saveSlideExports(imported, pptxPreviewDir);

  console.log(`Saved deck: ${deckPath}`);
  console.log(`Source previews: ${previewDir}`);
  console.log(`PPTX previews: ${pptxPreviewDir}`);
  console.log(`Layouts: ${layoutDir}`);
}

build().catch((error) => {
  console.error(error);
  process.exit(1);
});
