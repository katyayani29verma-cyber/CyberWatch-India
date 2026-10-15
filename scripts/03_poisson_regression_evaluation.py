from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import PoissonRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


# ---------------------------------------------------------
# 1. Set file locations
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "person2_submission"
    / "data"
    / "processed"
    / "cybercrime_model_features.csv"
)

METRICS_DIR = PROJECT_ROOT / "outputs" / "metrics"
PREDICTIONS_DIR = PROJECT_ROOT / "outputs" / "predictions"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"

METRICS_DIR.mkdir(parents=True, exist_ok=True)
PREDICTIONS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# 2. Load only safe rows for modelling
# ---------------------------------------------------------
df = pd.read_csv(INPUT_FILE)

model_df = df[
    (df["target_missing"] == False)
    & (df["previous_year_cases"].notna())
    & (df["boundary_break_flag"] == False)
].copy()

model_df["year"] = model_df["year"].astype(int)

print("\n--- POISSON REGRESSION EVALUATION ---")
print(f"Rows available for modelling: {len(model_df)}")


# ---------------------------------------------------------
# 3. Choose prediction inputs and target
# ---------------------------------------------------------
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

X_columns = numeric_features + categorical_features


# ---------------------------------------------------------
# 4. Prepare numeric and State/UT data
# ---------------------------------------------------------
numeric_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]
)

categorical_pipeline = Pipeline(
    steps=[
        ("one_hot_encoder", OneHotEncoder(handle_unknown="ignore")),
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        ("numeric", numeric_pipeline, numeric_features),
        ("categorical", categorical_pipeline, categorical_features),
    ],
    sparse_threshold=0,
)


# ---------------------------------------------------------
# 5. Test models year by year, always using earlier years
# ---------------------------------------------------------
test_years = [2021, 2022, 2023]

all_predictions = []
all_metrics = []

for test_year in test_years:
    train_df = model_df[model_df["year"] < test_year].copy()
    test_df = model_df[model_df["year"] == test_year].copy()

    X_train = train_df[X_columns]
    y_train = train_df[target_column]

    X_test = test_df[X_columns]
    y_test = test_df[target_column]

    # Baseline: predicted cases = previous year's cases
    baseline_predictions = test_df["previous_year_cases"].to_numpy()

    # Poisson Regression: appropriate for non-negative count outcomes
    poisson_model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            (
                "model",
                PoissonRegressor(
                    alpha=1.0,
                    max_iter=2000,
                ),
            ),
        ]
    )

    poisson_model.fit(X_train, y_train)

    poisson_predictions = poisson_model.predict(X_test)

    # Crime-case predictions cannot be negative.
    poisson_predictions = np.maximum(poisson_predictions, 0)

    # Save row-level predictions.
    year_predictions = test_df[
        ["state_ut_standard", "year", "target_reported_cases"]
    ].copy()

    year_predictions["baseline_prediction"] = baseline_predictions
    year_predictions["poisson_prediction"] = poisson_predictions

    year_predictions["baseline_absolute_error"] = np.abs(
        year_predictions["target_reported_cases"]
        - year_predictions["baseline_prediction"]
    )

    year_predictions["poisson_absolute_error"] = np.abs(
        year_predictions["target_reported_cases"]
        - year_predictions["poisson_prediction"]
    )

    all_predictions.append(year_predictions)

    # Calculate MAE and RMSE for both methods.
    for model_name, predictions in [
        ("Previous-year baseline", baseline_predictions),
        ("Poisson Regression", poisson_predictions),
    ]:
        mae = mean_absolute_error(y_test, predictions)
        rmse = mean_squared_error(y_test, predictions) ** 0.5

        all_metrics.append(
            {
                "model": model_name,
                "test_year": test_year,
                "rows_evaluated": len(test_df),
                "MAE": mae,
                "RMSE": rmse,
            }
        )


# ---------------------------------------------------------
# 6. Combine results and calculate overall performance
# ---------------------------------------------------------
predictions_df = pd.concat(all_predictions, ignore_index=True)
metrics_df = pd.DataFrame(all_metrics)

overall_metrics = []

for model_name, prediction_column in [
    ("Previous-year baseline", "baseline_prediction"),
    ("Poisson Regression", "poisson_prediction"),
]:
    overall_mae = mean_absolute_error(
        predictions_df["target_reported_cases"],
        predictions_df[prediction_column],
    )

    overall_rmse = mean_squared_error(
        predictions_df["target_reported_cases"],
        predictions_df[prediction_column],
    ) ** 0.5

    overall_metrics.append(
        {
            "model": model_name,
            "test_year": "Overall 2021-2023",
            "rows_evaluated": len(predictions_df),
            "MAE": overall_mae,
            "RMSE": overall_rmse,
        }
    )

metrics_df = pd.concat(
    [metrics_df, pd.DataFrame(overall_metrics)],
    ignore_index=True,
)


# ---------------------------------------------------------
# 7. Print and save numerical results
# ---------------------------------------------------------
print("\n--- POISSON REGRESSION VS BASELINE ---")
print(metrics_df.to_string(index=False))

print("\n--- LARGEST POISSON ERRORS ---")
largest_errors = (
    predictions_df.sort_values("poisson_absolute_error", ascending=False)
    .head(10)[
        [
            "state_ut_standard",
            "year",
            "target_reported_cases",
            "poisson_prediction",
            "poisson_absolute_error",
        ]
    ]
)
print(largest_errors.to_string(index=False))

metrics_path = METRICS_DIR / "poisson_vs_baseline_metrics_2021_2023.csv"
predictions_path = (
    PREDICTIONS_DIR / "poisson_vs_baseline_predictions_2021_2023.csv"
)

metrics_df.to_csv(metrics_path, index=False)
predictions_df.to_csv(predictions_path, index=False)


# ---------------------------------------------------------
# 8. Create actual-versus-predicted figure
# ---------------------------------------------------------
plt.figure(figsize=(9, 7))

plt.scatter(
    predictions_df["target_reported_cases"],
    predictions_df["baseline_prediction"],
    alpha=0.65,
    label="Previous-year baseline",
)

plt.scatter(
    predictions_df["target_reported_cases"],
    predictions_df["poisson_prediction"],
    alpha=0.65,
    label="Poisson Regression",
)

maximum_value = max(
    predictions_df["target_reported_cases"].max(),
    predictions_df["baseline_prediction"].max(),
    predictions_df["poisson_prediction"].max(),
)

plt.plot(
    [0, maximum_value],
    [0, maximum_value],
    linestyle="--",
    color="black",
    label="Perfect prediction",
)

plt.xlabel("Actual reported cybercrime cases")
plt.ylabel("Predicted reported cybercrime cases")
plt.title("Poisson Regression vs Previous-Year Baseline (2021–2023)")
plt.legend()
plt.tight_layout()

figure_path = FIGURES_DIR / "poisson_actual_vs_predicted_2021_2023.png"
plt.savefig(figure_path, dpi=300)
plt.close()

print(f"\nSaved metrics to: {METRICS_DIR.relative_to(PROJECT_ROOT)}")
print(f"Saved predictions to: {PREDICTIONS_DIR.relative_to(PROJECT_ROOT)}")
print(f"Saved figure to: {figure_path.reative_to(PROJECT_ROOT)}")