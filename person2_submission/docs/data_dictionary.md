# Data Dictionary

This dictionary covers the three canonical CSV outputs. The master is the fullest record; the analytical file is a compact subset; the modelling file separates the prediction target from candidate predictors.

## Master and analytical datasets
Files: `data/processed/cybercrime_master_2018_2023.csv` and `data/processed/cybercrime_model_input.csv`.

| Column | Meaning |
|---|---|
| `source_id` | Source identifier, expected to be S01 for the selected panel. |
| `source_table_key` | Identifier for the source table. |
| `state_ut_original` | State/UT label exactly as represented in the source CSV. |
| `sl_no_original` | Original source serial number, when present. |
| `row_type` | Source row type; retained for auditability. Selected rows are `state_ut`. |
| `block` | Source block/section, when present. |
| `year` | Calendar reporting year, 2018–2023. |
| `reported_cases_raw` | Parsed source field copied without numeric cleaning. |
| `raw_value_text` | Original textual representation of the reported value. |
| `measure_type` | Source measure description. |
| `category` | Measure category; selected panel is total cybercrime, not fraud-only. |
| `source_name` | Source description. |
| `source_file` | Name of source transcript/file recorded in S01. |
| `table_page` | Table/annex reference recorded with the source. |
| `source_url` | Source URL recorded in S01. |
| `notes` | Original source note, blank if none. |
| `state_ut_standard` | Standardised State/UT name from the naming reference. |
| `reported_cases` | Numeric analysis count; may remain missing if unresolved. |
| `quality_flag` | Empty for ordinary source values; `externally_verified_correction` for cited corrections. |
| `case_value_status` | `reported`, `reported_zero`, `missing_unresolved`, or `verified_external_correction`. |
| `state_ut_source_name` | State/UT name in the population source table. |
| `population_thousands` | Population as represented in the source projection table, in thousands. |
| `population_persons` | Population converted to persons (`population_thousands × 1000`). |
| `source_id_population` | Population-source identifier, when suffixing is required by the merge. |
| `source_url_population` | Official population-source URL. |
| `source_table_reference` | Population source table and page reference. |
| `boundary_comparability` | `current_boundary_series` or `historical_boundary_not_comparable`. Metadata, not a numeric feature. |
| `boundary_break_flag` | True when a row is flagged for the territorial-boundary issue. |
| `crime_rate_per_100k` | Cases divided by population persons × 100,000; blank if cases missing or boundary denominator incompatible. |
| `previous_year_cases` | Prior-year case count within State/UT; blank for first year or suppressed boundary transition. |
| `previous_year_crime_rate_per_100k` | Prior-year rate; blank if unavailable or suppressed. |
| `absolute_change` | Current cases minus prior-year cases; blank if either unavailable or boundary transition suppressed. |
| `annual_growth_pct` | Percentage change from previous year; blank if previous count is zero/missing or transition suppressed. |
| `rolling_3yr_avg_cases` | Trailing 3-year mean including current year; calculated only with three available case values. |
| `national_total_cases` | Sum of available/corrected State/UT cases in the panel for that year. |
| `national_share_pct` | State/UT cases as a percentage of that annual panel sum; missing case values remain missing. |

Note: because columns from the population input may collide with source fields, the exact merged population-provenance names are those visible in the CSV header; the script uses pandas suffixes to keep them distinct.

## Modelling dataset
File: `data/processed/cybercrime_model_features.csv`.

| Column | Meaning / use |
|---|---|
| `state_ut_standard` | State/UT identifier; encode appropriately for the chosen model. |
| `year` | Forecast year/time index. |
| `population_persons` | Population denominator available at the time of prediction. |
| `previous_year_cases` | Lagged case count; candidate predictor. |
| `previous_year_crime_rate_per_100k` | Lagged rate; candidate predictor. |
| `boundary_comparability` | Data-quality metadata; not a numeric predictor by default. |
| `boundary_break_flag` | Boundary warning; use for filtering/stratification, not as a substitute for data. |
| `target_reported_cases` | Outcome to predict. Never use as an input predictor. |
| `target_missing` | True when target is missing. Use to exclude unresolved targets from supervised training; never use as a predictor. |

## Audit files
- `input_inventory.csv`: input file purpose and preservation rules.
- `ladakh_correction_log.csv`: correction values and evidence citations.
- `national_total_reconciliation.csv`: original and corrected annual sums.
- `validation_checks.csv`: checks run by the script and their outcomes.
