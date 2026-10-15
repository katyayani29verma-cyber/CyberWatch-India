from pathlib import Path
import math

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

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

# Keep only safe rows for normal modelling.
usable = df[
    (~df["target_missing"])
    & (df["previous_year_cases"].notna())
    & (~df["boundary_break_flag"])
].copy()

# Features known before the target year's case count is observed.
numeric_features = [
    "year",
    "population_persons",
    "previous_year_cases",
    "previous_year_crime_rate_per_100k",
]

categorical_features = [
    "state_ut_standard",
]

target_column = "target_reported_cases"

# Numeric data is filled with the training median if needed, then scaled.
numeric_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]
)

# State/UT names are converted into machine-readable columns.
categorical_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("one_hot", OneHotEncoder(handle_unknown="ignore")),
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        ("numeric", numeric_pipeline, numeric_features),
        ("categorical", categorical_pipeline, categorical_features),
    ]
)

# Ridge Regression is a regularized version of Linear Regression.
# Regularization helps reduce overfitting in a small dataset.
ridge_model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", Ridge(alpha=10.0)),
    ]
)

results = []
metric_rows = []

# Chronological evaluation:
# Train on earlier years only, then test on the next future year.
for test_year in [2021, 2022, 2023]:
    train = usable[usable["year"] < test_year].copy()
    test = usable[usable["year"] == test_year].copy()

    X_train = train[numeric_features + categorical_features]
    y_train = train[target_column]

    X_test = test[numeric_features + categorical_features]
    y_test = test[target_column]

    ridge_model.fit(X_train, y_train)

    ridge_predictions = ridge_model.predict(X_test)

    # Case counts cannot be negative.
    ridge_predictions = np.maximum(ridge_predictions, 0)

    # Baseline prediction for direct comparison.
    baseline_predictions = test["previous_year_cases"].to_numpy()

    for model_name, predictions in [
        ("Previous-year baseline", baseline_predictions),
        ("Ridge Regression", ridge_predictions),
    ]:
        mae = mean_absolute_error(y_test, predictions)
        rmse = math.sqrt(mean_squared_error(y_test, predictions))

        metric_rows.append(
            {
                "model": model_name,
                "test_year": test_year,
                "rows_evaluated": len(test),
                "MAE": mae,
                "RMSE": rmse,
            }
        )

    test_results = test[
        [
            "state_ut_standard",
            "year",
            "target_reported_cases",
            "previous_year_cases",
        ]
    ].copy()

    test_results["baseline_prediction"] = baseline_predictions
    test_results["ridge_prediction"] = ridge_predictions
    test_results["baseline_absolute_error"] = (
        test_results["target_reported_cases"]
        - test_results["baseline_prediction"]
    ).abs()

    test_results["ridge_absolute_error"] = (
        test_results["target_reported_cases"]
        - test_results["ridge_prediction"]
    ).abs()

    results.append(test_results)

all_results = pd.concat(results, ignore_index=True)
metrics = pd.DataFrame(metric_rows)

# Add overall metrics for both models.
overall_rows = []

for model_name, prediction_column in [
    ("Previous-year baseline", "baseline_prediction"),
    ("Ridge Regression", "ridge_prediction"),
]:
    actual = all_results["target_reported_cases"]
    predicted = all_results[prediction_column]

    overall_rows.append(
        {
            "model": model_name,
            "test_year": "Overall 2021-2023",
            "rows_evaluated": len(all_results),
            "MAE": mean_absolute_error(actual, predicted),
            "RMSE": math.sqrt(mean_squared_error(actual, predicted)),
        }
    )

metrics = pd.concat(
    [metrics, pd.DataFrame(overall_rows)],
    ignore_index=True,
)

all_results.to_csv(
    PREDICTIONS_DIR / "ridge_vs_baseline_predictions_2021_2023.csv",
    index=False,
)

metrics.to_csv(
    METRICS_DIR / "ridge_vs_baseline_metrics_2021_2023.csv",
    index=False,
)

print("\n--- RIDGE REGRESSION VS BASELINE ---")
print(metrics.to_string(index=False))

print("\n--- LARGEST RIDGE ERRORS ---")
print(
    all_results.sort_values("ridge_absolute_error", ascending=False)
    .head(10)[
        [
            "state_ut_standard",
            "year",
            "target_reported_cases",
            "ridge_prediction",
            "ridge_absolute_error",
        ]
    ]
    .to_string(index=False)
)

sns.set_theme(style="whitegrid")

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

for ax, test_year in zip(axes, [2021, 2022, 2023]):
    group = all_results[all_results["year"] == test_year]

    sns.scatterplot(
        data=group,
        x="target_reported_cases",
        y="ridge_prediction",
        s=70,
        ax=ax,
    )

    maximum = max(
        group["target_reported_cases"].max(),
        group["ridge_prediction"].max(),
    )

    ax.plot(
        [0, maximum],
        [0, maximum],
        linestyle="--",
        color="red",
        label="Perfect prediction",
    )

    ax.set_title(f"Ridge: Actual vs Predicted ({test_year})")
    ax.set_xlabel("Actual reported cases")
    ax.set_ylabel("Ridge prediction")
    ax.legend()

plt.tight_layout()

figure_path = FIGURES_DIR / "ridge_actual_vs_predicted_2021_2023.png"
plt.savefig(figure_path, dpi=300, bbox_inches="tight")
plt.close()

print(f"\nSaved metrics to: {METRICS_DIR}")
print(f"Saved predictions to: {PREDICTIONS_DIR}")
print(f"Saved figure to: {figure_path}")