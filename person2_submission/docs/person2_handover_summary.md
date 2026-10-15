# Person 2 Handover Summary

## 1. What this work does
This submission turns the primary S01 series into a clean, traceable State/UT-year panel for total registered cybercrime cases from 2018 through 2023. The outputs are intended for descriptive analysis, charts, and a carefully designed downstream forecasting workflow.

The measure is **cases registered by police**, not complaints, victims, arrests, convictions, or monetary loss. Fraud-only tables are not mixed into the total-cybercrime series.

## 2. Deliverables
| Deliverable | Location | Purpose |
|---|---|---|
| Full master dataset | `data/processed/cybercrime_master_2018_2023.csv` | Source traceability, cleaned cases, population, engineered variables, and flags |
| Analytical dataset | `data/processed/cybercrime_model_input.csv` | Compact dataset for analysis and visualisation |
| Modelling dataset | `data/processed/cybercrime_model_features.csv` | Lagged predictors and separate prediction target |
| Input inventory | `data/processed/audit/input_inventory.csv` | Explains the limited input set and each input's role |
| Correction log | `data/processed/audit/ladakh_correction_log.csv` | Documents the four externally verified Ladakh values |
| Annual reconciliation | `data/processed/audit/national_total_reconciliation.csv` | Compares original parsed sums, corrected sums, and official reference totals |
| Validation results | `data/processed/audit/validation_checks.csv` | Machine-readable checks produced by the pipeline |
| Pipeline | `scripts/build_person2_dataset.py` | Rebuilds all three outputs and audit files |

## 3. Included source inputs
Only two Person 1 files are included: the S01 primary series and its State/UT naming reference. They are stored in `data/source_inputs/` and are never edited by the script. Other Person 1 files and helper scripts are excluded. The population values used for rate calculations and the correction log are separate inputs with provenance notes.

## 4. Main processing decisions
- Filter to `row_type = state_ut`, total cybercrime category, years 2018–2023.
- Standardise names through the supplied S01 naming reference.
- Keep `reported_cases_raw` and `raw_value_text` unchanged; create a separate numeric `reported_cases` field.
- Preserve unknown/missing values as missing. Never convert blanks or dashes to zero.
- Apply only the cited Ladakh corrections for 2020–2023: 1, 5, 3, and 1. Ladakh 2018–2019 remains unresolved.
- Merge population by standard State/UT and year, calculate crime rate per 100,000, national share, lagged cases/rate, absolute change, annual percentage growth, and a trailing three-year mean.
- Flag the Jammu & Kashmir/Ladakh boundary comparability issue and suppress rates/changes that would imply an invalid comparison.

## 5. How to use the modelling file safely
`target_reported_cases` is the value to predict. `target_missing` is a quality indicator. Neither is a predictor. Use only the lagged predictors and other features explicitly approved by the modelling team. Rows with a missing target must be excluded from supervised training/evaluation, not imputed as zero. Use chronological/time-based validation rather than random row splitting.

## 6. Known limitations
- Ladakh's 2018–2019 values are not resolved in the primary source; they remain missing.
- The population input is a structured extraction of official projection-table values, not the original PDF itself. The source URL and table reference are recorded per row and described in `population_source_notes.md`.
- Population projections are rounded and should not be described as observed census counts.
- The 2019 territorial reorganisation limits direct comparisons for historical Jammu & Kashmir/Ladakh rows.
- Structural and arithmetic checks do not independently prove every source value; official source documents should be checked manually before publication.

## 7. Reproduce and verify
From the submission root, run `python scripts/build_person2_dataset.py`. The pipeline checks row counts, key uniqueness, naming mappings, population matching, missingness, annual shares, correction flags, and the boundary break. Detailed results are in `processed_data_validation.md` and the audit CSVs.
