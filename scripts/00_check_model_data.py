from pathlib import Path
import pandas as pd

DATA_PATH = Path(
    "person2_submission/data/processed/cybercrime_model_features.csv"
)

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"\nCould not find this file:\n{DATA_PATH}\n\n"
        "Make sure person2_submission is inside your cyberwatch-india folder."
    )

df = pd.read_csv(DATA_PATH)

print("\n--- DATASET OVERVIEW ---")
print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(f"State/UTs: {df['state_ut_standard'].nunique()}")
print(f"Years: {sorted(df['year'].unique())}")

print("\n--- COLUMNS ---")
print(df.columns.tolist())

print("\n--- MISSING VALUES PER COLUMN ---")
print(df.isna().sum().sort_values(ascending=False))

print("\n--- ROWS WITH MISSING PREDICTION TARGET ---")
print(
    df[df["target_missing"]]
    .sort_values(["state_ut_standard", "year"])
    .to_string(index=False)
)

print("\n--- ROWS FLAGGED FOR J&K/LADAKH BOUNDARY CHANGE ---")
print(
    df[df["boundary_break_flag"]]
    .sort_values(["state_ut_standard", "year"])
    .to_string(index=False)
)

usable = df[
    (~df["target_missing"])
    & (df["previous_year_cases"].notna())
    & (~df["boundary_break_flag"])
].copy()

print("\n--- SAFE INITIAL MODELLING DATA ---")
print(f"Usable rows: {len(usable)}")

print("\nUsable rows by target year:")
print(usable.groupby("year").size())

print("\n--- FIRST FIVE SAFE ROWS ---")
print(usable.head().to_string(index=False))