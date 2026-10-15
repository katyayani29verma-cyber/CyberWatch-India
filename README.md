# CyberWatch India  
## State/UT-wise Cybercrime Trends, Statistical Analysis, and Forecasting

CyberWatch India is a reproducible research project analysing reported cybercrime cases across Indian States and Union Territories from 2018 to 2023.

The project combines source-traceable public records, documented data cleaning, exploratory analysis, statistical summaries, and chronological forecasting evaluation. It examines how reported cybercrime patterns differ across States/UTs when case counts, population-adjusted rates, and temporal changes are considered together.

## Research objectives

This project aims to:

- compile and document State/UT-level reported cybercrime data from official sources;
- create a clean, reproducible dataset for analysis;
- compare absolute reported case counts with population-adjusted crime rates;
- identify temporal and geographic patterns in reported cybercrime;
- evaluate forecasting methods for next-year reported cybercrime cases;
- report findings with clear limitations and without making unsupported causal claims.

## Study scope

- **Geographic coverage:** Indian States and Union Territories  
- **Analysis period:** 2018–2023  
- **Unit of analysis:** One State/UT in one year  
- **Primary outcome:** Reported cybercrime cases  
- **Primary forecasting task:** Predict next-year reported cybercrime cases  

The project analyses reported and registered cases. These figures do not represent every cybercrime incident experienced by residents.

## Repository structure

```text
cyberwatch-india/
├── person1_evidence/             # Source collection and evidence trail
├── person2_submission/           # Cleaning, population data, and feature preparation
├── person3_submission/           # Exploratory analysis, charts, and statistical outputs
├── scripts/                      # Person 4 modelling scripts
├── outputs/
│   ├── figures/                  # Generated charts
│   ├── metrics/                  # Model-evaluation tables
│   └── predictions/              # Row-level model predictions
├── requirements.txt
├── .gitignore
└── README.md
```

## Team contributions

| Person | Contributor | Responsibility |
|---|---|---|
| Person 1 | Jinay | Data collection, raw source files, extraction transcripts, source inventory, and evidence documentation |
| Person 2 | Anushka | Data cleaning, State/UT standardisation, population data, derived features, validation checks, and modelling dataset preparation |
| Person 3 | Prisha | Exploratory data analysis, descriptive statistics, correlation analysis, and visualisations |
| Person 4 | Katyayani | Forecasting workflow, model evaluation, model selection, statistical testing, forecast outputs, and final project integration |

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
Person 4: forecasting, model comparison, statistical analysis, and final report
```

## Important data decisions

### State/UT naming

Raw source names are preserved in Person 1’s files. Person 2 created standard State/UT names for analysis while retaining the original-source traceability.

### Jammu & Kashmir and Ladakh

The 2019 territorial reorganisation affects comparability between historical Jammu & Kashmir figures and later separate Jammu & Kashmir/Ladakh figures.

For forecasting evaluation, rows marked with `boundary_break_flag = True` are excluded. Missing Ladakh records for 2018 and 2019 are not treated as zero and are never imputed.

### Population data

Population values are documented official projections. Population-adjusted rates should therefore be interpreted as estimated reported-case rates, not exact census-based rates.

## Exploratory analysis

The project includes:

- national reported-cybercrime trend;
- top States/UTs by 2023 reported cases;
- top States/UTs by 2023 reported crime rate per 100,000 population;
- State/UT trend charts;
- State-year heatmap;
- annual growth analysis;
- ranking comparison chart;
- histogram and boxplot of reported crime rates;
- population-versus-cases scatter plot;
- Pearson correlation matrix.

Correlation and visual patterns are descriptive. They do not establish causation.

## Forecasting methodology

The forecasting target is:

\[
\text{Reported cybercrime cases}_{s,t}
\]

where \(s\) represents a State/UT and \(t\) represents a year.

Only information available before the target year is used as a predictor:

- previous-year reported cases;
- previous-year reported crime rate per 100,000 population;
- population;
- State/UT identity;
- year.

The following were never used as prediction inputs:

- target-year reported cases;
- target-year crime rate;
- target-year growth;
- target-year national share;
- target-year rolling averages.

This prevents target leakage.

### Evaluation design

Models are evaluated chronologically:

| Training data | Test year |
|---|---|
| Earlier valid years | 2021 |
| Earlier valid years | 2022 |
| Earlier valid years | 2023 |

This simulates the real forecasting situation: the model can only learn from years that occurred before the year it predicts.

### Models evaluated

1. **Previous-year baseline**

\[
\hat{Y}_{s,t} = Y_{s,t-1}
\]

2. Ridge Regression  
3. Poisson Regression  
4. Random Forest Regression  

Models are compared using:

\[
\text{MAE} =
\frac{1}{n}
\sum_{i=1}^{n}
|y_i-\hat{y}_i|
\]

\[
\text{RMSE} =
\sqrt{
\frac{1}{n}
\sum_{i=1}^{n}
(y_i-\hat{y}_i)^2
}
\]

Lower values indicate better predictive accuracy.

## Model-selection result

The previous-year baseline was selected as the final forecasting model because it produced the lowest overall prediction error on unseen 2021–2023 data.

| Model | Overall MAE | Overall RMSE | Decision |
|---|---:|---:|---|
| Previous-year baseline | **543.99** | **1437.99** | Selected |
| Random Forest Regression | 622.48 | 1653.32 | Rejected |
| Ridge Regression | 666.20 | 1542.58 | Rejected |
| Poisson Regression | 852.19 | 2164.52 | Rejected |

A simpler model was selected because it generalized better to future years than the more complex alternatives.

## Running the project

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the modelling workflow in order:

```powershell
python scripts/00_check_model_data.py
python scripts/01_baseline_evaluation.py
python scripts/02_ridge_regression_evaluation.py
python scripts/03_poisson_regression_evaluation.py
python scripts/04_random_forest_evaluation.py
python scripts/05_create_final_model_comparison.py
```

Generated results are saved in:

```text
outputs/metrics/
outputs/predictions/
outputs/figures/
```

## Key limitations

- Reported cybercrime cases do not capture all cybercrime incidents.
- Differences in awareness, registration practices, and reporting systems may affect comparisons.
- Population values are projections.
- The 2018–2023 period provides only a limited number of annual observations.
- Jammu & Kashmir/Ladakh historical boundary changes reduce long-term comparability.
- Forecasting models predict reported counts, not actual cybercrime prevalence.
- Correlation and model feature importance do not establish causation.

## Current status

Completed:

- source evidence package;
- cleaned and validated dataset;
- exploratory charts and descriptive statistics;
- chronological evaluation of four forecasting approaches;
- final model-selection table and figure.

Planned next steps:

- hypothesis-testing outputs;
- 2024 reported-case forecast using the selected baseline;
- residual analysis and forecast uncertainty summary;
- final research paper and presentation.