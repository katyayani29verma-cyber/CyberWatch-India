from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

from scipy.stats import spearmanr, wilcoxon
from statsmodels.stats.multitest import multipletests


# ---------------------------------------------------------
# 1. File locations
# ---------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "person2_submission"
    / "data"
    / "processed"
    / "cybercrime_master_2018_2023.csv"
)

STATISTICS_DIR = PROJECT_ROOT / "outputs" / "statistics"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"

STATISTICS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# 2. Load data
# ---------------------------------------------------------
df = pd.read_csv(INPUT_FILE)

df["year"] = df["year"].astype(int)

# Convert safely whether the CSV stores True/False as text or booleans.
boundary_ok = (
    df["boundary_break_flag"]
    .astype(str)
    .str.strip()
    .str.lower()
    .eq("false")
)

# Only records without the documented J&K/Ladakh boundary break
# may be used in the paired 2019-versus-2023 tests.
comparable_df = df[boundary_ok].copy()

print("\n--- HYPOTHESIS TESTING ---")
print(f"Total rows in master dataset: {len(df)}")
print(f"Rows without boundary-break flag: {len(comparable_df)}")


# ---------------------------------------------------------
# 3. Create matched 2019 and 2023 State/UT pairs
# ---------------------------------------------------------
def create_matched_pairs(value_column):
    selected = comparable_df[
        comparable_df["year"].isin([2019, 2023])
    ].copy()

    pairs = selected.pivot_table(
        index="state_ut_standard",
        columns="year",
        values=value_column,
        aggfunc="first",
    )

    pairs = pairs.dropna(subset=[2019, 2023]).copy()
    pairs.columns.name = None

    pairs["difference_2023_minus_2019"] = (
        pairs[2023] - pairs[2019]
    )

    return pairs


rate_pairs = create_matched_pairs("crime_rate_per_100k")
case_pairs = create_matched_pairs("reported_cases")

print("\n--- MATCHED COMPARABLE STATE/UT PAIRS ---")
print(f"Rate test pairs: {len(rate_pairs)}")
print(f"Case-count test pairs: {len(case_pairs)}")


# ---------------------------------------------------------
# 4. Test H1: Did reported rates rise from 2019 to 2023?
#
# H0: median(rate_2023 - rate_2019) = 0
# H1: median(rate_2023 - rate_2019) > 0
# ---------------------------------------------------------
rate_wilcoxon = wilcoxon(
    rate_pairs[2023],
    rate_pairs[2019],
    alternative="greater",
)

rate_median_difference = (
    rate_pairs["difference_2023_minus_2019"].median()
)


# ---------------------------------------------------------
# 5. Test H2: Did reported case counts rise from 2019 to 2023?
#
# H0: median(cases_2023 - cases_2019) = 0
# H1: median(cases_2023 - cases_2019) > 0
# ---------------------------------------------------------
case_wilcoxon = wilcoxon(
    case_pairs[2023],
    case_pairs[2019],
    alternative="greater",
)

case_median_difference = (
    case_pairs["difference_2023_minus_2019"].median()
)


# ---------------------------------------------------------
# 6. Test H3: Was population associated with cases in 2023?
#
# H0: Spearman rho = 0
# H1: Spearman rho != 0
# ---------------------------------------------------------
data_2023 = df[
    (df["year"] == 2023)
    & (df["population_persons"].notna())
    & (df["reported_cases"].notna())
].copy()

spearman_result = spearmanr(
    data_2023["population_persons"],
    data_2023["reported_cases"],
)


# ---------------------------------------------------------
# 7. Holm correction for three hypothesis tests
# ---------------------------------------------------------
raw_p_values = [
    rate_wilcoxon.pvalue,
    case_wilcoxon.pvalue,
    spearman_result.pvalue,
]

rejected, adjusted_p_values, _, _ = multipletests(
    raw_p_values,
    alpha=0.05,
    method="holm",
)


# ---------------------------------------------------------
# 8. Create and save paper-ready results table
# ---------------------------------------------------------
results_df = pd.DataFrame(
    [
        {
            "test_id": "H1",
            "test_name": "Wilcoxon signed-rank test",
            "research_question": (
                "Did comparable State/UT reported cybercrime rates "
                "increase from 2019 to 2023?"
            ),
            "sample_size": len(rate_pairs),
            "statistic": rate_wilcoxon.statistic,
            "effect_estimate": rate_median_difference,
            "effect_measure": (
                "Median rate change per 100,000 population"
            ),
            "raw_p_value": rate_wilcoxon.pvalue,
            "holm_adjusted_p_value": adjusted_p_values[0],
            "significant_at_0_05": bool(rejected[0]),
        },
        {
            "test_id": "H2",
            "test_name": "Wilcoxon signed-rank test",
            "research_question": (
                "Did comparable State/UT reported cybercrime case counts "
                "increase from 2019 to 2023?"
            ),
            "sample_size": len(case_pairs),
            "statistic": case_wilcoxon.statistic,
            "effect_estimate": case_median_difference,
            "effect_measure": (
                "Median reported-case change"
            ),
            "raw_p_value": case_wilcoxon.pvalue,
            "holm_adjusted_p_value": adjusted_p_values[1],
            "significant_at_0_05": bool(rejected[1]),
        },
        {
            "test_id": "H3",
            "test_name": "Spearman rank correlation",
            "research_question": (
                "Across State/UTs in 2023, was population associated "
                "with reported cybercrime cases?"
            ),
            "sample_size": len(data_2023),
            "statistic": spearman_result.statistic,
            "effect_estimate": spearman_result.statistic,
            "effect_measure": "Spearman correlation coefficient",
            "raw_p_value": spearman_result.pvalue,
            "holm_adjusted_p_value": adjusted_p_values[2],
            "significant_at_0_05": bool(rejected[2]),
        },
    ]
)

results_path = STATISTICS_DIR / "hypothesis_test_results.csv"
results_df.to_csv(results_path, index=False)

paired_values_path = (
    STATISTICS_DIR / "paired_2019_2023_rate_values.csv"
)
rate_pairs.reset_index().to_csv(paired_values_path, index=False)


# ---------------------------------------------------------
# 9. Graph 1: paired State/UT rate change, 2019 to 2023
# ---------------------------------------------------------
plot_pairs = rate_pairs.sort_values(
    "difference_2023_minus_2019"
).reset_index()

fig, ax = plt.subplots(figsize=(10, 12))

for _, row in plot_pairs.iterrows():
    color = "#2E8B57" if row[2023] >= row[2019] else "#C0392B"

    ax.plot(
        [2019, 2023],
        [row[2019], row[2023]],
        color=color,
        alpha=0.45,
        linewidth=1.3,
    )

ax.scatter(
    [2019] * len(plot_pairs),
    plot_pairs[2019],
    color="#4C78A8",
    label="2019 rate",
    zorder=3,
)

ax.scatter(
    [2023] * len(plot_pairs),
    plot_pairs[2023],
    color="#F58518",
    label="2023 rate",
    zorder=3,
)

ax.set_title(
    "Comparable State/UT Cybercrime Rates: 2019 vs 2023"
)
ax.set_xlabel("Year")
ax.set_ylabel("Reported cases per 100,000 population")
ax.set_xticks([2019, 2023])
ax.grid(axis="y", linestyle="--", alpha=0.35)
ax.legend()

plt.tight_layout()

rate_figure_path = (
    FIGURES_DIR / "hypothesis_paired_rates_2019_2023.png"
)
plt.savefig(rate_figure_path, dpi=300)
plt.close()


# ---------------------------------------------------------
# 10. Graph 2: Spearman rank association, 2023
# ---------------------------------------------------------
rank_data = data_2023[
    [
        "state_ut_standard",
        "population_persons",
        "reported_cases",
    ]
].copy()

rank_data["population_rank"] = rank_data[
    "population_persons"
].rank(method="average")

rank_data["reported_cases_rank"] = rank_data[
    "reported_cases"
].rank(method="average")

fig, ax = plt.subplots(figsize=(9, 7))

ax.scatter(
    rank_data["population_rank"],
    rank_data["reported_cases_rank"],
    color="#4C78A8",
    alpha=0.75,
)

for _, row in rank_data.iterrows():
    ax.annotate(
        row["state_ut_standard"],
        (
            row["population_rank"],
            row["reported_cases_rank"],
        ),
        fontsize=6,
        alpha=0.7,
        xytext=(3, 3),
        textcoords="offset points",
    )

rho = spearman_result.statistic
adjusted_p = adjusted_p_values[2]

ax.set_title(
    "Population Rank vs Reported Cybercrime Case Rank, 2023"
)
ax.set_xlabel("Population rank across State/UTs")
ax.set_ylabel("Reported-case rank across State/UTs")

ax.text(
    0.03,
    0.97,
    (
        f"Spearman rho = {rho:.3f}\n"
        f"Holm-adjusted p = {adjusted_p:.4g}"
    ),
    transform=ax.transAxes,
    verticalalignment="top",
    bbox={
        "boxstyle": "round",
        "facecolor": "white",
        "alpha": 0.85,
    },
)

ax.grid(linestyle="--", alpha=0.35)

plt.tight_layout()

spearman_figure_path = (
    FIGURES_DIR
    / "hypothesis_population_cases_spearman_2023.png"
)
plt.savefig(spearman_figure_path, dpi=300)
plt.close()


# ---------------------------------------------------------
# 11. Print results
# ---------------------------------------------------------
print("\n--- HYPOTHESIS-TEST RESULTS ---")
print(
    results_df[
        [
            "test_id",
            "test_name",
            "sample_size",
            "statistic",
            "effect_estimate",
            "raw_p_value",
            "holm_adjusted_p_value",
            "significant_at_0_05",
        ]
    ].to_string(index=False)
)

print("\nSaved files:")
print(f"- {results_path.relative_to(PROJECT_ROOT)}")
print(f"- {paired_values_path.relative_to(PROJECT_ROOT)}")
print(f"- {rate_figure_path.relative_to(PROJECT_ROOT)}")
print(f"- {spearman_figure_path.relative_to(PROJECT_ROOT)}")