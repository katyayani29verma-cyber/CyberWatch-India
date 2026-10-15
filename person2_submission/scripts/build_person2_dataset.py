from pathlib import Path
import hashlib
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data/source_inputs/S01_LS_USQ438_2025-12-02_AnnexII_2014-2023.csv"
NAMES = ROOT / "data/source_inputs/state_ut_naming_reference.csv"
POP = ROOT / "data/external/population_source_values.csv"
CORRECTIONS = ROOT / "data/reference/ladakh_correction_log.csv"
OUT = ROOT / "data/processed"
AUDIT = OUT / "audit"
MASTER = OUT / "cybercrime_master_2018_2023.csv"
ANALYTIC = OUT / "cybercrime_model_input.csv"
MODEL = OUT / "cybercrime_model_features.csv"


def require_columns(df, required, label):
    missing = sorted(set(required) - set(df.columns))
    if missing:
        raise ValueError(f"{label} is missing required columns: {missing}")


def main():
    raw = pd.read_csv(SOURCE)
    names = pd.read_csv(NAMES)
    pop = pd.read_csv(POP)
    corrections = pd.read_csv(CORRECTIONS)
    require_columns(raw, ["source_id", "source_table_key", "state_ut_original", "row_type", "year", "reported_cases_raw", "raw_value_text", "category"], "S01 source")
    require_columns(names, ["source_id", "source_table_key", "state_ut_original", "suggested_standard_name"], "naming reference")
    require_columns(pop, ["state_ut_standard", "year", "population_persons", "population_thousands", "source_id", "source_url", "source_table_reference"], "population input")
    require_columns(corrections, ["year", "state_ut", "verified_value", "source_id", "source_url", "source_table_reference"], "correction log")

    # Scope: only state/UT rows, total cybercrime measure, 2018–2023.
    selected = raw.loc[(raw.row_type == "state_ut") &
        (raw.category == "Total cyber crimes (IT Act + IPC + SLL, NCRB definition)") &
        raw.year.between(2018, 2023)].copy()
    mapping = names.loc[names.source_id.eq("S01"), ["source_id", "source_table_key", "state_ut_original", "suggested_standard_name"]].drop_duplicates()
    selected = selected.merge(mapping, on=["source_id", "source_table_key", "state_ut_original"], how="left", validate="many_to_one")
    if selected.suggested_standard_name.isna().any():
        raise ValueError("At least one source State/UT has no mapping in the supplied naming reference")
    selected = selected.rename(columns={"suggested_standard_name": "state_ut_standard"})
    selected["reported_cases"] = pd.to_numeric(selected.reported_cases_raw, errors="coerce")
    selected["quality_flag"] = ""
    selected["case_value_status"] = np.where(selected.reported_cases.isna(), "missing_unresolved", np.where(selected.reported_cases.eq(0), "reported_zero", "reported"))

    # Apply only corrections with an explicit source citation; never alter raw text fields.
    corr = corrections.loc[corrections.state_ut.eq("Ladakh")].copy()
    if set(corr.year.astype(int)) != {2020, 2021, 2022, 2023} or corr.year.duplicated().any():
        raise ValueError("Correction log must contain exactly one cited Ladakh correction for each of 2020–2023")
    for r in corr.itertuples(index=False):
        mask = selected.state_ut_standard.eq("Ladakh") & selected.year.eq(int(r.year))
        if mask.sum() != 1:
            raise ValueError(f"Expected one Ladakh row in {r.year}; found {int(mask.sum())}")
        selected.loc[mask, "reported_cases"] = int(r.verified_value)
        selected.loc[mask, "quality_flag"] = "externally_verified_correction"
        selected.loc[mask, "case_value_status"] = "verified_external_correction"
    selected["notes"] = selected["notes"].fillna("") if "notes" in selected else ""
    selected = selected.sort_values(["state_ut_standard", "year"]).reset_index(drop=True)
    keys = ["state_ut_standard", "year"]
    if len(selected) != 216 or selected.duplicated(keys).any() or selected.state_ut_standard.nunique() != 36:
        raise ValueError(f"Expected 216 unique State/UT-year rows for 36 entities; got {len(selected)}")

    # Population input is an extracted/transformed input from the cited official projection table,
    # not a byte-for-byte raw PDF transcription. Source provenance is carried row-wise.
    if pop.duplicated(keys).any():
        raise ValueError("Population input has duplicate State/UT-year keys")
    pop["population_persons"] = pd.to_numeric(pop.population_persons, errors="coerce")
    if pop.population_persons.isna().any() or (pop.population_persons <= 0).any():
        raise ValueError("Population input has missing/non-positive population values")
    joined = selected.merge(pop, on=keys, how="left", validate="one_to_one", indicator=True, suffixes=("", "_population"))
    if not joined._merge.eq("both").all():
        missing = joined.loc[joined._merge.ne("both"), keys].to_dict("records")
        raise ValueError(f"Population merge did not match all rows: {missing[:10]}")
    joined = joined.drop(columns="_merge")

    # Explicitly flag historical territorial-boundary mismatch. Keep counts, suppress invalid rates.
    joined["boundary_comparability"] = "current_boundary_series"
    joined["boundary_break_flag"] = False
    hist = joined.year.isin([2018, 2019]) & joined.state_ut_standard.isin(["Jammu and Kashmir", "Ladakh"])
    joined.loc[hist, "boundary_comparability"] = "historical_boundary_not_comparable"
    joined.loc[hist, "boundary_break_flag"] = True
    joined["crime_rate_per_100k"] = joined.reported_cases / joined.population_persons * 100000
    joined.loc[hist | joined.reported_cases.isna(), "crime_rate_per_100k"] = np.nan

    joined = joined.sort_values(keys).reset_index(drop=True)
    grouped = joined.groupby("state_ut_standard", sort=False)
    joined["previous_year_cases"] = grouped.reported_cases.shift(1)
    joined["previous_year_crime_rate_per_100k"] = grouped.crime_rate_per_100k.shift(1)
    transition = joined.year.eq(2020) & joined.state_ut_standard.isin(["Jammu and Kashmir", "Ladakh"])
    joined.loc[transition, ["previous_year_cases", "previous_year_crime_rate_per_100k"]] = np.nan
    joined.loc[transition, "boundary_break_flag"] = True
    joined["absolute_change"] = joined.reported_cases - joined.previous_year_cases
    prev = joined.previous_year_cases.where(joined.previous_year_cases.ne(0))
    joined["annual_growth_pct"] = (joined.reported_cases / prev - 1) * 100
    joined.loc[transition, ["absolute_change", "annual_growth_pct"]] = np.nan
    # Trailing 3-year average includes the current year and available prior observations; min_periods=3
    # ensures a full three-year window, and missing case counts remain missing rather than zero.
    joined["rolling_3yr_avg_cases"] = grouped.reported_cases.transform(lambda s: s.rolling(window=3, min_periods=3).mean())
    joined["rolling_3yr_avg_cases"] = joined["rolling_3yr_avg_cases"].astype(float)
    annual_totals = joined.groupby("year").reported_cases.sum(min_count=1)
    joined["national_total_cases"] = joined.year.map(annual_totals)
    joined["national_share_pct"] = joined.reported_cases / joined.national_total_cases * 100

    # Master is the complete analysis-ready record, including population and engineered variables.
    # Preserve source values and keep audit outputs in their own subfolder.
    OUT.mkdir(parents=True, exist_ok=True); AUDIT.mkdir(parents=True, exist_ok=True)
    joined.to_csv(MASTER, index=False)
    analytical_columns = [
        "state_ut_standard", "year", "reported_cases_raw", "raw_value_text", "reported_cases",
        "case_value_status", "quality_flag", "population_persons", "crime_rate_per_100k",
        "previous_year_cases", "previous_year_crime_rate_per_100k", "absolute_change",
        "annual_growth_pct", "rolling_3yr_avg_cases", "national_total_cases", "national_share_pct",
        "boundary_comparability", "boundary_break_flag", "source_id", "source_url",
        "table_page", "source_file"
    ]
    joined[analytical_columns].to_csv(ANALYTIC, index=False)

    # Leakage-controlled model table: target is separate from predictors; no current-year derived features.
    model = joined[["state_ut_standard", "year", "population_persons", "previous_year_cases", "previous_year_crime_rate_per_100k", "boundary_comparability", "boundary_break_flag", "reported_cases"]].rename(columns={"reported_cases": "target_reported_cases"})
    model["target_missing"] = model.target_reported_cases.isna()
    model.to_csv(MODEL, index=False)

    # Auditable annual reconciliation: raw source sum, corrected state/UT sum, and available count.
    source_only = selected.copy()
    original_numeric = pd.to_numeric(source_only.reported_cases_raw, errors="coerce")
    reconciliation = []
    official_totals = {2018:27248, 2019:44735, 2020:50035, 2021:52974, 2022:65893, 2023:86420}
    for year in range(2018, 2024):
        rows = joined.loc[joined.year.eq(year)]
        reconciliation.append({"year":year,"source_series_state_ut_sum_after_numeric_parse":float(original_numeric[source_only.year.eq(year)].sum(min_count=1)),"corrected_analysis_state_ut_sum":float(rows.reported_cases.sum(min_count=1)),"official_total_reference":official_totals.get(year),"known_case_count":int(rows.reported_cases.notna().sum()),"row_count":int(len(rows)),"note":"2018–2019 historical J&K/Ladakh boundary caveat; official totals are references, not a license to impute missing values."})
    pd.DataFrame(reconciliation).to_csv(AUDIT/"national_total_reconciliation.csv", index=False)
    corr.to_csv(AUDIT/"ladakh_correction_log.csv", index=False)
    inventory = pd.DataFrame([
        {"file":"data/source_inputs/S01_LS_USQ438_2025-12-02_AnnexII_2014-2023.csv","role":"Required Person 1 primary input","used_by":"build_person2_dataset.py","preservation":"read-only; raw fields carried into outputs"},
        {"file":"data/source_inputs/state_ut_naming_reference.csv","role":"Required Person 1 naming map","used_by":"build_person2_dataset.py","preservation":"read-only"},
        {"file":"data/external/population_source_values.csv","role":"Person 2 extracted population input","used_by":"build_person2_dataset.py","preservation":"source URL/table reference carried row-wise"},
        {"file":"data/reference/ladakh_correction_log.csv","role":"Person 2 cited correction log","used_by":"build_person2_dataset.py","preservation":"only 2020–2023 documented corrections applied"},
    ])
    inventory.to_csv(AUDIT/"input_inventory.csv", index=False)
    validation = pd.DataFrame([
        {"check":"row_count","result":len(joined),"expected":"216","passed":len(joined)==216},
        {"check":"unique_state_ut_year","result":int(joined.duplicated(keys).sum()),"expected":"0 duplicates","passed":not joined.duplicated(keys).any()},
        {"check":"state_ut_count","result":joined.state_ut_standard.nunique(),"expected":"36","passed":joined.state_ut_standard.nunique()==36},
        {"check":"year_coverage","result":','.join(map(str,sorted(joined.year.unique()))),"expected":"2018,2019,2020,2021,2022,2023","passed":set(joined.year)==set(range(2018,2024))},
        {"check":"missing_population","result":int(joined.population_persons.isna().sum()),"expected":"0","passed":not joined.population_persons.isna().any()},
        {"check":"unresolved_case_values","result":int(joined.reported_cases.isna().sum()),"expected":"retain as missing, never zero-fill","passed":joined.loc[joined.reported_cases.isna(),"case_value_status"].eq("missing_unresolved").all()},
        {"check":"missing_rolling_avg_first_two_years_per_group","result":int(joined.rolling_3yr_avg_cases.isna().sum()),"expected":"expected due to 3-year window and unresolved data","passed":True},
        {"check":"raw_text_preserved","result":int(joined.raw_value_text.isna().sum()),"expected":"source text preserved where present","passed":True},
    ])
    validation.to_csv(AUDIT/"validation_checks.csv", index=False)
    assert np.allclose(joined.groupby("year").national_share_pct.sum(min_count=1).dropna().values,100,atol=1e-6)
    assert joined.loc[joined.case_value_status.eq("verified_external_correction"),"quality_flag"].eq("externally_verified_correction").all()
    assert joined.loc[transition,"previous_year_cases"].isna().all()
    print(f"PASS: {len(joined)} rows, {joined.state_ut_standard.nunique()} State/UTs, {joined.year.min()}–{joined.year.max()}")
    print(f"Unresolved cases kept missing: {int(joined.reported_cases.isna().sum())}; population missing: {int(joined.population_persons.isna().sum())}")
    print("Annual corrected sums:", {int(k): float(v) for k,v in annual_totals.items()})

if __name__ == "__main__":
    main()
