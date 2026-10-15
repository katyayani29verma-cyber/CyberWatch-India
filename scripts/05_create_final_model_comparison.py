from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------------------------------
# 1. File locations
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
METRICS_DIR = PROJECT_ROOT / "outputs" / "metrics"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# 2. Load overall rows from every model evaluation
# ---------------------------------------------------------
files = {
    "Baseline": METRICS_DIR / "baseline_metrics_2021_2023.csv",
    "Ridge Regression": METRICS_DIR / "ridge_vs_baseline_metrics_2021_2023.csv",
    "Poisson Regression": METRICS_DIR / "poisson_vs_baseline_metrics_2021_2023.csv",
    "Random Forest Regression": (
        METRICS_DIR
        / "random_forest_vs_baseline_metrics_2021_2023.csv"
    ),
}

rows = []

for source_name, file_path in files.items():
    metrics = pd.read_csv(file_path)

    overall_rows = metrics[
        metrics["test_year"] == "Overall 2021-2023"
    ].copy()

    # Files comparing against the baseline contain its repeated row.
    if source_name == "Baseline":
        overall_rows = overall_rows[
            overall_rows["model"] == "Previous-year baseline"
        ]
    else:
        overall_rows = overall_rows[
            overall_rows["model"] != "Previous-year baseline"
        ]

    rows.append(overall_rows)

comparison_df = pd.concat(rows, ignore_index=True)

comparison_df = comparison_df[
    ["model", "test_year", "rows_evaluated", "MAE", "RMSE"]
].sort_values("MAE").reset_index(drop=True)

comparison_df["selection_decision"] = "Rejected"

comparison_df.loc[
    comparison_df["model"] == "Previous-year baseline",
    "selection_decision",
] = "Selected final model"


# ---------------------------------------------------------
# 3. Save final comparison table
# ---------------------------------------------------------
output_csv = METRICS_DIR / "final_model_comparison_2021_2023.csv"
comparison_df.to_csv(output_csv, index=False)

print("\n--- FINAL MODEL COMPARISON ---")
print(comparison_df.to_string(index=False))


# ---------------------------------------------------------
# 4. Make MAE and RMSE comparison figure
# ---------------------------------------------------------
plot_df = comparison_df.sort_values("MAE")

fig, axes = plt.subplots(1, 2, figsize=(13, 5))

colors = [
    "#2E8B57" if model == "Previous-year baseline" else "#888888"
    for model in plot_df["model"]
]

axes[0].bar(plot_df["model"], plot_df["MAE"], color=colors)
axes[0].set_title("Model Comparison: Mean Absolute Error")
axes[0].set_ylabel("MAE: lower is better")
axes[0].tick_params(axis="x", rotation=25)

axes[1].bar(plot_df["model"], plot_df["RMSE"], color=colors)
axes[1].set_title("Model Comparison: Root Mean Squared Error")
axes[1].set_ylabel("RMSE: lower is better")
axes[1].tick_params(axis="x", rotation=25)

fig.suptitle("CyberWatch India: Chronological Model Evaluation (2021–2023)")
plt.tight_layout()

output_figure = FIGURES_DIR / "final_model_comparison_2021_2023.png"
plt.savefig(output_figure, dpi=300, bbox_inches="tight")
plt.close()

print(f"\nSaved final comparison CSV to: {output_csv.relative_to(PROJECT_ROOT)}")
print(f"Saved final comparison figure to: {output_figure.relative_to(PROJECT_ROOT)}")