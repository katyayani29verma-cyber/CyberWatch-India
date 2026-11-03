from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------------------------------
# 1. File locations
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "person2_submission"
    / "data"
    / "processed"
    / "cybercrime_model_features.csv"
)

FORECASTS_DIR = PROJECT_ROOT / "outputs" / "forecasts"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
STATISTICS_DIR = PROJECT_ROOT / "outputs" / "statistics"

FORECASTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
STATISTICS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# 2. Load safe modelling data
# ---------------------------------------------------------
df = pd.read_csv(INPUT_FILE)
df["year"] = df["year"].astype(int)

safe_df = df[
    (df["target_missing"] == False)
    & (df["previous_year_cases"].notna())
    & (df["boundary_break_flag"] == False)
].copy()


# ---------------------------------------------------------
# 3. Recreate historical baseline errors: 2021–2023
#
# Baseline formula:
# forecast for year t = actual cases in year t-1
# ---------------------------------------------------------
validation_df = safe_df[
    safe_df["year"].isin([2021, 2022, 2023])
].copy()

validation_df["baseline_prediction"] = (
    validation_df["previous_year_cases"]
)

validation_df["residual"] = (
    validation_df["target_reported_cases"]
    - validation_df["baseline_prediction"]
)

validation_df["absolute_error"] = (
    validation_df["residual"].abs()
)

# An empirical 80% interval uses the 10th and 90th percentiles
# of historical signed forecast errors.
lower_residual = validation_df["residual"].quantile(0.10)
upper_residual = validation_df["residual"].quantile(0.90)

historical_coverage = (
    (
        validation_df["target_reported_cases"]
        >= validation_df["baseline_prediction"] + lower_residual
    )
    &
    (
        validation_df["target_reported_cases"]
        <= validation_df["baseline_prediction"] + upper_residual
    )
).mean()

print("\n--- BASELINE UNCERTAINTY FROM 2021–2023 ERRORS ---")
print(f"Validation rows: {len(validation_df)}")
print(f"10th-percentile residual: {lower_residual:.2f}")
print(f"90th-percentile residual: {upper_residual:.2f}")
print(f"Historical interval coverage: {historical_coverage:.1%}")


# ---------------------------------------------------------
# 4. Create 2024 State/UT forecast
#
# For the selected baseline:
# predicted cases in 2024 = actual cases in 2023
# ---------------------------------------------------------
forecast_df = safe_df[
    safe_df["year"] == 2023
].copy()

forecast_df = forecast_df[
    [
        "state_ut_standard",
        "population_persons",
        "target_reported_cases",
    ]
].rename(
    columns={
        "target_reported_cases": "reported_cases_2023",
        "population_persons": "population_2023",
    }
)

forecast_df["forecast_year"] = 2024
forecast_df["forecasted_reported_cases"] = (
    forecast_df["reported_cases_2023"]
)

forecast_df["interval_lower_80pct"] = np.maximum(
    0,
    forecast_df["forecasted_reported_cases"] + lower_residual,
)

forecast_df["interval_upper_80pct"] = np.maximum(
    0,
    forecast_df["forecasted_reported_cases"] + upper_residual,
)

forecast_df["forecast_method"] = (
    "Previous-year baseline: forecasted 2024 cases equal reported 2023 cases"
)

forecast_df["uncertainty_note"] = (
    "Empirical 80% residual interval based on pooled baseline errors "
    "from chronological 2021-2023 validation; not a causal or formal "
    "prediction interval."
)

forecast_df = forecast_df.sort_values(
    "forecasted_reported_cases",
    ascending=False,
).reset_index(drop=True)

forecast_df.insert(0, "forecast_rank", range(1, len(forecast_df) + 1))


# ---------------------------------------------------------
# 5. Save forecast and historical residual data
# ---------------------------------------------------------
forecast_path = (
    FORECASTS_DIR / "baseline_forecast_2024_state_ut.csv"
)

residual_path = (
    STATISTICS_DIR / "baseline_residuals_2021_2023.csv"
)

uncertainty_summary_path = (
    STATISTICS_DIR / "baseline_uncertainty_summary.csv"
)

forecast_df.to_csv(forecast_path, index=False)

validation_df[
    [
        "state_ut_standard",
        "year",
        "target_reported_cases",
        "baseline_prediction",
        "residual",
        "absolute_error",
    ]
].to_csv(residual_path, index=False)

uncertainty_summary = pd.DataFrame(
    [
        {
            "model": "Previous-year baseline",
            "validation_years": "2021-2023",
            "validation_rows": len(validation_df),
            "interval_level": "80%",
            "lower_residual_quantile": lower_residual,
            "upper_residual_quantile": upper_residual,
            "historical_coverage": historical_coverage,
            "interpretation": (
                "Empirical pooled residual interval. It describes past "
                "baseline error variation and is not a formal confidence interval."
            ),
        }
    ]
)

uncertainty_summary.to_csv(
    uncertainty_summary_path,
    index=False,
)


# ---------------------------------------------------------
# 6. Graph 1: 2024 forecast for top 15 State/UTs
# ---------------------------------------------------------
top_15 = forecast_df.head(15).sort_values(
    "forecasted_reported_cases",
    ascending=True,
)

fig, ax = plt.subplots(figsize=(11, 8))

error_lower = (
    top_15["forecasted_reported_cases"]
    - top_15["interval_lower_80pct"]
)

error_upper = (
    top_15["interval_upper_80pct"]
    - top_15["forecasted_reported_cases"]
)

ax.barh(
    top_15["state_ut_standard"],
    top_15["forecasted_reported_cases"],
    xerr=[error_lower, error_upper],
    capsize=3,
    color="#2E8B57",
    alpha=0.85,
)

ax.set_title(
    "Baseline Forecast of Reported Cybercrime Cases for 2024\n"
    "Top 15 State/UTs by Forecasted Cases"
)
ax.set_xlabel("Forecasted reported cases")
ax.set_ylabel("State/UT")
ax.ticklabel_format(axis="x", style="plain")
ax.grid(axis="x", linestyle="--", alpha=0.35)

plt.tight_layout()

forecast_figure_path = (
    FIGURES_DIR / "baseline_forecast_2024_top15.png"
)

plt.savefig(forecast_figure_path, dpi=300)
plt.close()


# ---------------------------------------------------------
# 7. Graph 2: residual diagnostics from 2021–2023
# ---------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 7))

colors = np.where(
    validation_df["residual"] >= 0,
    "#2E8B57",
    "#C0392B",
)

ax.scatter(
    validation_df["target_reported_cases"],
    validation_df["residual"],
    c=colors,
    alpha=0.75,
)

ax.axhline(0, color="black", linestyle="--", linewidth=1)

ax.set_title(
    "Previous-Year Baseline Residuals: Chronological Validation (2021–2023)"
)
ax.set_xlabel("Actual reported cybercrime cases")
ax.set_ylabel("Residual = Actual cases − Baseline prediction")
ax.grid(linestyle="--", alpha=0.35)

plt.tight_layout()

residual_figure_path = (
    FIGURES_DIR / "baseline_residuals_2021_2023.png"
)

plt.savefig(residual_figure_path, dpi=300)
plt.close()


# ---------------------------------------------------------
# 8. Print final results
# ---------------------------------------------------------
print("\n--- 2024 FORECAST CREATED ---")
print(
    forecast_df[
        [
            "forecast_rank",
            "state_ut_standard",
            "reported_cases_2023",
            "forecasted_reported_cases",
            "interval_lower_80pct",
            "interval_upper_80pct",
        ]
    ].head(10).to_string(index=False)
)

print("\nSaved files:")
print(f"- {forecast_path.relative_to(PROJECT_ROOT)}")
print(f"- {residual_path.relative_to(PROJECT_ROOT)}")
print(f"- {uncertainty_summary_path.relative_to(PROJECT_ROOT)}")
print(f"- {forecast_figure_path.relative_to(PROJECT_ROOT)}")
print(f"- {residual_figure_path.relative_to(PROJECT_ROOT)}")
