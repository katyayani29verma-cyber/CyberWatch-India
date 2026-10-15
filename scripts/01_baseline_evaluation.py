from pathlib import Path
import math

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import mean_absolute_error, mean_squared_error

DATA_PATH = Path(
    "person2_submission/data/processed/cybercrime_model_features.csv"
)

METRICS_DIR = Path("outputs/metrics")
PREDICTIONS_DIR = Path("outputs/predictions")
FIGURES_DIR = Path("outputs/figures")

METRICS_DIR.mkdir(parents=True, exist_ok=True)
PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)

# Keep only records that are safe for normal modelling and evaluation.
usable = df[
    (~df["target_missing"])
    & (df["previous_year_cases"].notna())
    & (~df["boundary_break_flag"])
].copy()

# We will use 2021-2023 as the main evaluation years.
# Earlier years are retained for later model training.
evaluation = usable[usable["year"].isin([2021, 2022, 2023])].copy()

# Naive baseline: predict that the current year equals the previous year.
evaluation["baseline_prediction"] = evaluation["previous_year_cases"]

# Calculate prediction errors.
evaluation["error"] = (
    evaluation["target_reported_cases"]
    - evaluation["baseline_prediction"]
)

evaluation["absolute_error"] = evaluation["error"].abs()

# Save State/UT-level baseline predictions.
prediction_columns = [
    "state_ut_standard",
    "year",
    "previous_year_cases",
    "target_reported_cases",
    "baseline_prediction",
    "error",
    "absolute_error",
]

evaluation[prediction_columns].to_csv(
    PREDICTIONS_DIR / "baseline_predictions_2021_2023.csv",
    index=False,
)

# Calculate one set of metrics for each test year.
metric_rows = []

for year, group in evaluation.groupby("year"):
    actual = group["target_reported_cases"]
    predicted = group["baseline_prediction"]

    mae = mean_absolute_error(actual, predicted)
    rmse = math.sqrt(mean_squared_error(actual, predicted))

    metric_rows.append(
        {
            "model": "Previous-year baseline",
            "test_year": year,
            "rows_evaluated": len(group),
            "MAE": mae,
            "RMSE": rmse,
        }
    )

# Add overall metrics across all evaluation years.
overall_actual = evaluation["target_reported_cases"]
overall_predicted = evaluation["baseline_prediction"]

metric_rows.append(
    {
        "model": "Previous-year baseline",
        "test_year": "Overall 2021-2023",
        "rows_evaluated": len(evaluation),
        "MAE": mean_absolute_error(overall_actual, overall_predicted),
        "RMSE": math.sqrt(
            mean_squared_error(overall_actual, overall_predicted)
        ),
    }
)

metrics = pd.DataFrame(metric_rows)

metrics.to_csv(
    METRICS_DIR / "baseline_metrics_2021_2023.csv",
    index=False,
)

print("\n--- PREVIOUS-YEAR BASELINE RESULTS ---")
print(metrics.to_string(index=False))

print("\nLargest baseline errors:")
print(
    evaluation.sort_values("absolute_error", ascending=False)
    .head(10)[
        [
            "state_ut_standard",
            "year",
            "target_reported_cases",
            "baseline_prediction",
            "absolute_error",
        ]
    ]
    .to_string(index=False)
)

# Create actual-versus-predicted plots for each evaluation year.
sns.set_theme(style="whitegrid")

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

for ax, year in zip(axes, [2021, 2022, 2023]):
    group = evaluation[evaluation["year"] == year]

    sns.scatterplot(
        data=group,
        x="target_reported_cases",
        y="baseline_prediction",
        s=70,
        ax=ax,
    )

    maximum = max(
        group["target_reported_cases"].max(),
        group["baseline_prediction"].max(),
    )

    ax.plot(
        [0, maximum],
        [0, maximum],
        linestyle="--",
        color="red",
        label="Perfect prediction",
    )

    ax.set_title(f"Baseline: Actual vs Predicted ({year})")
    ax.set_xlabel("Actual reported cases")
    ax.set_ylabel("Predicted reported cases")
    ax.legend()

plt.tight_layout()

figure_path = FIGURES_DIR / "baseline_actual_vs_predicted_2021_2023.png"
plt.savefig(figure_path, dpi=300, bbox_inches="tight")
plt.close()

print(f"\nSaved metrics to: {METRICS_DIR}")
print(f"Saved predictions to: {PREDICTIONS_DIR}")
print(f"Saved figure to: {figure_path}")