# Data Cleaning Log

## 1. Scope and source inputs
The analysis period is 2018–2023. The primary source is `data/source_inputs/S01_LS_USQ438_2025-12-02_AnnexII_2014-2023.csv`. The only other Person 1 input retained is `data/source_inputs/state_ut_naming_reference.csv`, which maps source spellings to standard State/UT names. Both are read-only. Population values are in `data/external/population_source_values.csv`; the separate correction record is in `data/reference/ladakh_correction_log.csv`.

The pipeline selects only `row_type=state_ut` and category `Total cyber crimes (IT Act + IPC + SLL, NCRB definition)`. Aggregate totals and fraud-only records are excluded.

## 2. Cleaning and traceability
1. Load S01 and validate required columns.
2. Filter the six analysis years and the State/UT total-cybercrime records.
3. Join the S01 name reference on `source_id`, `source_table_key`, and `state_ut_original`; stop if any name is unmapped.
4. Convert `reported_cases_raw` into a separate numeric `reported_cases` column. Keep `reported_cases_raw` and `raw_value_text` untouched.
5. Assign `case_value_status`: `reported`, `reported_zero`, `missing_unresolved`, or `verified_external_correction`.
6. Merge population one-to-one by standard State/UT and year. Stop if population is missing, duplicated, or non-positive.
7. Calculate analysis features and create explicit territorial-boundary flags.
8. Write the master, analytical and modelling datasets plus audit CSVs.

## 3. Missing values and zeros
A blank or non-numeric source value remains missing unless a cited correction applies. A numeric zero reported by the source remains zero. No blanket fill operation is used. Missing case counts produce missing rates and are not treated as zero for national shares or model targets.

## 4. Ladakh correction rule
The S01 primary series does not provide usable Ladakh values for the selected years. The separate correction log documents corroborating official PIB/MHA tables for:

| Year | Applied case count | Evidence |
|---:|---:|---|
| 2020 | 1 | PIB/MHA Annexure-I, PRID 2112244 |
| 2021 | 5 | PIB/MHA Annexure-I, PRID 2198253 |
| 2022 | 3 | PIB/MHA Annexure-I, PRID 2198253 |
| 2023 | 1 | PIB/MHA Annexure-I, PRID 2198253 |

Sources: https://www.pib.gov.in/PressReleaseIframePage.aspx?PRID=2112244&lang=2&reg=48 and https://www.pib.gov.in/PressReleasePage.aspx?PRID=2198253&lang=1&reg=1

The correction changes only the analysis field. The original reported text stays unchanged, and the corrected row receives `quality_flag=externally_verified_correction` and `case_value_status=verified_external_correction`. Ladakh 2018–2019 stays missing; no estimate is invented.

## 5. Population and engineered features
Population is converted from thousands to persons in the supplied extracted values. The source URL and table reference are preserved for each row. The calculation fields are:
- `crime_rate_per_100k = reported_cases / population_persons × 100000`
- `national_total_cases` = sum of available/corrected State/UT case counts for that year
- `national_share_pct = reported_cases / national_total_cases × 100`
- `previous_year_cases` and `previous_year_crime_rate_per_100k` = within-State/UT one-year lag
- `absolute_change = reported_cases − previous_year_cases`
- `annual_growth_pct = (reported_cases / previous_year_cases − 1) × 100`, undefined when the prior value is zero or missing
- `rolling_3yr_avg_cases` = trailing three-year arithmetic mean, only when all three case values in the window are present

## 6. Jammu & Kashmir/Ladakh boundary break
The 2019 territorial reorganisation affects comparability. Jammu & Kashmir and Ladakh in 2018–2019 are marked `historical_boundary_not_comparable`; rates are suppressed where the available population denominator does not represent the historical boundary. The 2020 lag, absolute change and growth are suppressed for these entities to prevent a cross-boundary change from being interpreted as a valid trend. Case counts themselves are not silently rewritten for this reason.

## 7. Reconciliation and validation
The audit reconciliation keeps the parsed source series sum separate from the corrected analysis sum and the published reference total. For 2018–2019, source sums equal 27,248 and 44,735. For 2020–2023, corrected sums are 50,035, 52,974, 65,893 and 86,420. These are arithmetic checks and do not remove the historical boundary limitation.

Run `python scripts/build_person2_dataset.py` to repeat the cleaning. The script does not modify either included source input.
