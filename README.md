# CyberWatch India

## State/UT-wise Cybercrime Trends, Statistical Analysis, and Forecasting

CyberWatch India is a reproducible research project analysing reported cybercrime cases across Indian States and Union Territories from 2018 to 2023.

The project combines source-traceable public records, documented data cleaning, exploratory analysis, statistical testing, chronological forecasting evaluation, and a 2024 State/UT-level forecast.

## Research objectives

This project aims to:

- collect and document State/UT-level reported cybercrime data from official sources;
- create a clean and reproducible dataset;
- compare absolute reported case counts with population-adjusted crime rates;
- identify geographic and temporal patterns in reported cybercrime;
- test selected statistical hypotheses using boundary-aware data;
- evaluate forecasting models for next-year reported cybercrime cases;
- report findings with clear limitations and without unsupported causal claims.

## Study scope

| Item | Scope |
|---|---|
| Geographic coverage | Indian States and Union Territories |
| Analysis period | 2018–2023 |
| Unit of analysis | One State/UT in one year |
| Primary outcome | Reported cybercrime cases |
| Forecasting task | Predict 2024 reported cybercrime cases |

The project analyses reported and registered cases. These figures do not represent every cybercrime incident experienced by residents.

## Repository structure

```text
cyberwatch-india/
├── person1_evidence/             # Source collection and evidence trail
├── person2_submission/           # Cleaning, population data, and feature preparation
├── person3_submission/           # EDA charts, notebook, and statistical outputs
├── scripts/                      # Data checks, model evaluation, tests, and forecast scripts
├── docs/
│   └── person4_forecasting_and_statistics.md
├── outputs/
│   ├── figures/                  # EDA, model, hypothesis-test, and forecast charts
│   ├── forecasts/                # 2024 State/UT forecast
│   ├── metrics/                  # Model-evaluation tables
│   ├── predictions/              # Row-level model predictions
│   └── statistics/               # Hypothesis tests, residuals, and uncertainty files
├── requirements.txt
├── .gitignore
└── README.md
```

## Team contributions

| Person | Contributor | Responsibility |
|---|---|---|
| Person 1 | Jinay | Raw-data collection, extraction transcripts, source inventory, evidence trail, and source documentation |
| Person 2 | Anushka | Data cleaning, State/UT standardisation, population data, feature engineering, validation checks, and modelling dataset preparation |
| Person 3 | Prisha | Exploratory analysis, descriptive statistics, correlation analysis, charts, and notebook outputs |
| Person 4 | Katyayani | Forecasting workflow, model evaluation, boundary-aware exclusions, hypothesis testing, 2024 forecast, and final project integration |

## Data workflow

```text
Official source records
        ↓
Person 1: raw data and evidence trail
        ↓
Person 2: cleaned and validated analytical dataset
        ↓
Person 3: exploratory analysis and visualisations
        ↓
Person 4: statistical testing, forecasting, model comparison, and final results
```

## Data sources and reproducibility

Person 1’s evidence package contains:

- source-wise raw CSV files;
- extraction transcripts;
- source inventory;
- extraction log;
- source download register;
- State/UT naming reference;
- validation sum checks;
- cross-source comparison;
- raw-data rebuild script.

Refer to:

```text
person1_evidence/docs/source_inventory.csv
person1_evidence/docs/extraction_log.md
person1_evidence/docs/source_download_register.md
```

Person 2’s package contains the cleaned dataset, population source values, boundary flags, validation files, data dictionary, and rebuild script.

## Important data decisions

### State/UT naming

Raw source names are preserved in Person 1’s source files. Person 2 created standard State/UT names for analysis while retaining traceability to original records.

### Jammu & Kashmir and Ladakh boundary change

The 2019 territorial reorganisation affects comparability between historical Jammu & Kashmir figures and later separate Jammu & Kashmir and Ladakh figures.

For modelling and paired statistical tests, records were excluded when:

```text
boundary_break_flag = True
```

Missing Ladakh records for 2018 and 2019 were not treated as zero and were never imputed.

### Population data

Population values are documented official projections. Population-adjusted rates should be interpreted as estimated reported-case rates, not exact census-based rates.

## Exploratory analysis

Person 3 produced exploratory outputs including:

- national reported-cybercrime trend;
- top States/UTs by 2023 reported cases;
- top States/UTs by reported cybercrime rate per 100,000 population;
- State/UT trend charts;
- State-year heatmap;
- annual growth analysis;
- ranking comparison chart;
- crime-rate histogram and boxplot;
- population-versus-cases scatter plot;
- correlation heatmap.

Charts and descriptive statistics are available in:

```text
person3_submission/
```

Correlation and visual patterns are descriptive. They do not establish causation.

## Forecasting methodology

The forecasting target is reported cybercrime cases for State/UT $s$ in year $t$:

$$
Y_{s,t}
$$

Only information available before the target year was considered as a potential model input:

- previous-year reported cases;
- previous-year reported crime rate per 100,000 population;
- population;
- State/UT identity;
- year.

The following target-year variables were excluded to prevent target leakage:

- target-year reported cases;
- target-year crime rate;
- target-year growth;
- target-year national share;
- target-year rolling average.

## Chronological evaluation design

Models were evaluated using chronological train-test splits.

| Test year | Training data |
|---|---|
| 2021 | Earlier valid years only |
| 2022 | Earlier valid years only |
| 2023 | Earlier valid years only |

This reflects the real forecasting situation: a model may use past information but cannot access the year it is trying to predict.

## Models evaluated

### 1. Previous-year baseline

The baseline predicts that next-year reported cases equal the most recent reported value:

$$
\hat{Y}_{s,t} = Y_{s,t-1}
$$

### 2. Ridge Regression

Ridge Regression used lagged case counts, previous-year crime rates, population, year, and State/UT identity with regularisation.

### 3. Poisson Regression

Poisson Regression was tested because reported cybercrime cases are non-negative counts.

### 4. Random Forest Regression

Random Forest Regression was tested to assess whether non-linear relationships improved forecasting performance.

## Model evaluation metrics

Models were compared using Mean Absolute Error (MAE) and Root Mean Squared Error (RMSE).

$$
\text{MAE} =
\frac{1}{n}
\sum_{i=1}^{n}
|y_i-\hat{y}_i|
$$

$$
\text{RMSE} =
\sqrt{
\frac{1}{n}
\sum_{i=1}^{n}
(y_i-\hat{y}_i)^2
}
$$

Lower MAE and RMSE indicate better predictive accuracy.

## Model-selection result

The previous-year baseline was selected because it produced the lowest overall error on unseen 2021–2023 data.

| Model | Overall MAE | Overall RMSE | Decision |
|---|---:|---:|---|
| Previous-year baseline | **543.99** | **1437.99** | Selected |
| Random Forest Regression | 622.48 | 1653.32 | Rejected |
| Ridge Regression | 666.20 | 1542.58 | Rejected |
| Poisson Regression | 852.19 | 2164.52 | Rejected |

The more complex models did not improve future-year prediction accuracy. The selected baseline generalized better with the available short State/UT time series.

## Hypothesis testing

Three hypothesis tests were conducted using boundary-aware data. Holm correction was used to adjust for multiple testing.

| Test | Sample | Result |
|---|---:|---|
| Wilcoxon signed-rank test: 2019 vs 2023 reported cybercrime rate | 34 comparable State/UTs | Median increase: 0.90 per 100,000; adjusted $p = 0.0000813$ |
| Wilcoxon signed-rank test: 2019 vs 2023 reported cybercrime cases | 34 comparable State/UTs | Median increase: 77 cases; adjusted $p = 0.000344$ |
| Spearman population–cases association, 2023 | 36 State/UTs | $\rho = 0.850$; adjusted $p < 0.001$ |

The results indicate that comparable State/UTs generally had higher reported cybercrime rates and reported case counts in 2023 than in 2019. Population had a strong positive association with reported case counts in 2023.

These findings describe observed patterns in reported records. They do not prove that population, policy, reporting awareness, or another factor caused cybercrime changes.

## 2024 forecast

The selected baseline forecast uses each State/UT’s reported 2023 count as its 2024 forecast:

$$
\hat{Y}_{s,2024} = Y_{s,2023}
$$

The highest forecasted reported-case counts are:

| Forecast rank | State/UT | Forecasted reported cases, 2024 |
|---:|---|---:|
| 1 | Karnataka | 21,889 |
| 2 | Telangana | 18,236 |
| 3 | Uttar Pradesh | 10,794 |
| 4 | Maharashtra | 8,103 |
| 5 | Bihar | 4,450 |
| 6 | Tamil Nadu | 4,121 |
| 7 | Kerala | 3,295 |
| 8 | Rajasthan | 2,435 |
| 9 | Odisha | 2,348 |
| 10 | Andhra Pradesh | 2,341 |

The complete forecast is available at:

```text
outputs/forecasts/baseline_forecast_2024_state_ut.csv
```

## Forecast uncertainty

An empirical 80% residual reference interval was calculated from pooled baseline errors during chronological 2021–2023 validation.

$$
\text{Residual}
=
\text{Actual cases}
-
\text{Baseline prediction}
$$

| Measure | Value |
|---|---:|
| Validation predictions | 108 |
| 10th-percentile residual | −125.60 |
| 90th-percentile residual | 1090.60 |
| Historical interval coverage | 79.6% |

This is a pooled empirical reference range, not a formal confidence interval or a state-specific guarantee. Forecast errors varied substantially across State/UTs, especially for some high-count states.

## Key outputs

```text
outputs/metrics/final_model_comparison_2021_2023.csv
outputs/figures/final_model_comparison_2021_2023.png

outputs/statistics/hypothesis_test_results.csv
outputs/statistics/paired_2019_2023_rate_values.csv
outputs/figures/hypothesis_paired_rates_2019_2023.png
outputs/figures/hypothesis_population_cases_spearman_2023.png

outputs/forecasts/baseline_forecast_2024_state_ut.csv
outputs/statistics/baseline_residuals_2021_2023.csv
outputs/statistics/baseline_uncertainty_summary.csv
outputs/figures/baseline_forecast_2024_top15.png
outputs/figures/baseline_residuals_2021_2023.png
```

A detailed Person 4 methodology and results document is available at:

```text
docs/person4_forecasting_and_statistics.md
```

## Running the project

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the Person 4 workflow in order:

```powershell
python scripts/00_check_model_data.py
python scripts/01_baseline_evaluation.py
python scripts/02_ridge_regression_evaluation.py
python scripts/03_poisson_regression_evaluation.py
python scripts/04_random_forest_evaluation.py
python scripts/05_create_final_model_comparison.py
python scripts/06_hypothesis_tests.py
python scripts/07_create_2024_baseline_forecast.py
```

Generated files are saved under:

```text
outputs/metrics/
outputs/predictions/
outputs/figures/
outputs/statistics/
outputs/forecasts/
```

## Requirements

The project uses:

```text
pandas
numpy
matplotlib
seaborn
scikit-learn
scipy
statsmodels
joblib
```

Install all packages through:

```powershell
python -m pip install -r requirements.txt
```

## Limitations

- Reported cybercrime cases do not capture all cybercrime incidents.
- Differences in awareness, registration practices, and reporting systems may affect comparisons.
- Population values are projections.
- The study period contains only six annual observations.
- Jammu & Kashmir/Ladakh boundary changes reduce long-term comparability.
- Forecasts concern reported counts, not actual cybercrime prevalence.
- Correlation and model results do not establish causation.
- The selected baseline may not capture sudden future changes.
- The pooled residual reference interval is not state-specific.

## Project status

Completed:

- source evidence package and raw-data documentation;
- cleaned and validated State/UT dataset;
- population-adjusted rate calculations and quality flags;
- exploratory charts and descriptive statistics;
- chronological evaluation of four forecasting approaches;
- final model-selection table and chart;
- hypothesis testing with Holm-adjusted p-values;
- 2024 State/UT-level forecast;
- residual analysis and empirical uncertainty summary;
- reproducible scripts and repository documentation.

The remaining submission deliverables are the final research paper and presentation.