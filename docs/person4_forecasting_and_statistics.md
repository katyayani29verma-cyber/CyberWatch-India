# Person 4: Statistical Testing and Forecasting Results

## Purpose

This document describes the statistical testing, forecasting evaluation, final model selection, and 2024 reported-cybercrime forecast for the CyberWatch India project.

The analysis uses Person 2’s cleaned and feature-engineered State/UT dataset for 2018–2023.

## Data used for modelling

The modelling dataset contains 216 State/UT-year observations:

$$
36\text{ State/UTs} \times 6\text{ years} = 216\text{ rows}
$$

Unsafe records were excluded from forecasting evaluation when they had:

- a missing target value;
- a missing previous-year reported-case value; or
- a Jammu & Kashmir/Ladakh boundary-break flag.

This resulted in 176 safe modelling rows.

Ladakh records for 2018–2019 were not treated as zero. Historical Jammu & Kashmir/Ladakh transition records were excluded because pre-reorganisation Jammu & Kashmir cannot be directly compared with later separate Jammu & Kashmir and Ladakh records.

## Forecasting approach

The task was to predict reported cybercrime cases for a State/UT in year $t$ using only information available before year $t$.

Candidate predictor variables included:

- previous-year reported cases;
- previous-year reported crime rate per 100,000 population;
- population;
- State/UT identity;
- year.

Target-year case counts, crime rates, growth, national share, and rolling averages were excluded from model inputs to prevent target leakage.

## Chronological evaluation

Models were evaluated with chronological train-test splits:

| Test year | Training data |
|---|---|
| 2021 | Earlier valid years |
| 2022 | Earlier valid years |
| 2023 | Earlier valid years |

This approach reflects the real forecasting setting because a model may only use past information when predicting a future year.

## Models evaluated

### Previous-year baseline

The baseline predicted that the next year’s reported cases would equal the latest observed value:

$$
\hat{Y}_{s,t} = Y_{s,t-1}
$$

### Ridge Regression

Ridge Regression used lagged case counts, previous-year rates, population, year, and State/UT identity with coefficient regularisation.

### Poisson Regression

Poisson Regression was evaluated because reported cybercrime cases are non-negative counts.

### Random Forest Regression

Random Forest Regression was evaluated to test whether non-linear relationships improved forecasting accuracy.

## Model-selection results

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

Lower values indicate better forecasting performance.

| Model | Overall MAE | Overall RMSE | Decision |
|---|---:|---:|---|
| Previous-year baseline | **543.99** | **1437.99** | Selected |
| Random Forest Regression | 622.48 | 1653.32 | Rejected |
| Ridge Regression | 666.20 | 1542.58 | Rejected |
| Poisson Regression | 852.19 | 2164.52 | Rejected |

The previous-year baseline was selected because it produced the lowest overall MAE and RMSE on unseen 2021–2023 data.

More complex models did not improve predictive accuracy. This may reflect the limited annual history available for each State/UT and sudden changes in reported-case patterns.

## Hypothesis testing

### H1: Change in reported cybercrime rates

A one-sided Wilcoxon signed-rank test compared reported crime rates per 100,000 population in 2019 and 2023 across 34 comparable State/UTs.

$$
H_0:
\text{Median}(\text{Rate}_{2023} - \text{Rate}_{2019}) = 0
$$

$$
H_1:
\text{Median}(\text{Rate}_{2023} - \text{Rate}_{2019}) > 0
$$

Result:

- Median rate increase: **0.90 reported cases per 100,000 population**
- Holm-adjusted p-value: **0.0000813**
- Decision: Reject $H_0$

Reported cybercrime rates were significantly higher in 2023 than in 2019 among the comparable State/UTs.

### H2: Change in reported cybercrime case counts

A one-sided Wilcoxon signed-rank test compared reported cybercrime case counts in 2019 and 2023 across 34 comparable State/UTs.

$$
H_0:
\text{Median}(\text{Cases}_{2023} - \text{Cases}_{2019}) = 0
$$

$$
H_1:
\text{Median}(\text{Cases}_{2023} - \text{Cases}_{2019}) > 0
$$

Result:

- Median case-count increase: **77 reported cases**
- Holm-adjusted p-value: **0.000344**
- Decision: Reject $H_0$

Reported cybercrime case counts were significantly higher in 2023 than in 2019 among the comparable State/UTs.

### H3: Population and reported cybercrime cases

A two-sided Spearman rank-correlation test examined the relationship between population and reported cybercrime cases across 36 State/UTs in 2023.

$$
H_0: \rho_s = 0
$$

$$
H_1: \rho_s \neq 0
$$

Result:

- Spearman correlation: **0.850**
- Holm-adjusted p-value: **1.586 × 10⁻¹⁰**
- Decision: Reject $H_0$

Population and reported cybercrime cases showed a strong positive association in 2023. This association does not establish that population caused cybercrime.

## 2024 forecast

The selected baseline model was trained through the latest available observation year. The 2024 forecast is:

$$
\hat{Y}_{s,2024} = Y_{s,2023}
$$

The largest forecasted reported-case counts are:

| Forecast rank | State/UT | Forecasted 2024 reported cases |
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

The complete State/UT forecast is available in:

```text
outputs/forecasts/baseline_forecast_2024_state_ut.csv
```

## Forecast uncertainty

An empirical 80% residual reference interval was calculated from pooled baseline residuals across chronological 2021–2023 validation.

$$
\text{Residual} =
\text{Actual cases}
-
\text{Baseline prediction}
$$

The 10th and 90th percentile residuals were:

| Measure | Value |
|---|---:|
| 10th-percentile residual | −125.60 |
| 90th-percentile residual | 1090.60 |
| Historical coverage | 79.6% |

This reference interval describes historical baseline error variation. It is not a formal confidence interval and should be interpreted cautiously because forecast errors were larger for some high-count States/UTs.

## Key limitations

- Reported cases do not represent all cybercrime incidents.
- Reporting practices, registration systems, and awareness may affect observed counts.
- Population values are projections.
- Only six annual observations are available per State/UT.
- Jammu & Kashmir/Ladakh boundary changes reduce historical comparability.
- Correlation does not establish causation.
- The selected baseline predicts persistence from the most recent observed year and may miss sudden changes.
- The pooled residual range does not provide state-specific uncertainty estimates.

## Output files

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