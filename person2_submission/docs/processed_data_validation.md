# Processed Data Validation Report

## 1. Validation approach
The canonical script runs structural and arithmetic checks when it rebuilds the outputs. The machine-readable results are saved to `data/processed/audit/validation_checks.csv`. This report explains what those checks mean and what they do not prove.

## 2. Expected panel structure
| Check | Expected result | Meaning |
|---|---:|---|
| Analysis years | 2018–2023 | Six consecutive reporting years |
| State/UT entities | 36 | Standardised entities represented in each year |
| Rows | 216 | 36 entities × 6 years |
| Duplicate State/UT-year keys | 0 | Exactly one selected row per entity and year |
| Unmatched population rows | 0 | Every panel row has a population record |
| Missing population values | 0 | Population input is complete and positive |

## 3. Run result
The pipeline was run after assembling this package. It produced 216 rows for 36 State/UTs over 2018–2023, with no duplicate State/UT-year keys and no missing population matches. The annual corrected panel sums were:

| Year | Corrected panel sum | Published reference total |
|---:|---:|---:|
| 2018 | 27,248 | 27,248 |
| 2019 | 44,735 | 44,735 |
| 2020 | 50,035 | 50,035 |
| 2021 | 52,974 | 52,974 |
| 2022 | 65,893 | 65,893 |
| 2023 | 86,420 | 86,420 |

The annual totals are reconciliation references, not a reason to impute an individual missing State/UT value. See the audit CSV for source-parsed sums and corrected sums separately.

## 4. Missingness and rolling window
Two case-count targets remain unresolved: Ladakh 2018 and Ladakh 2019. They are represented as missing, not zero. The trailing three-year average is missing whenever a full three-year window of case counts is not available; this is expected for the first two years and for windows containing unresolved case values.

## 5. Boundary treatment
Jammu & Kashmir and Ladakh in 2018–2019 are marked `historical_boundary_not_comparable`. Historical rates are suppressed where the available population denominator does not match the historical boundary. The 2020 previous-year lag, absolute change, and growth are suppressed for Jammu & Kashmir and Ladakh so the 2019-to-2020 territorial change is not misrepresented as an ordinary annual change.

## 6. Model leakage checks
The modelling table contains `target_reported_cases` and `target_missing` as separate target/quality columns. Neither should be used as a predictor. Current-year case rate, national share, annual growth, absolute change, and rolling average are excluded from the modelling table to avoid target leakage. First-year lags remain missing because 2017 is outside the selected panel. Use chronological validation and exclude missing targets from supervised training/evaluation.

## 7. What is not established by these checks
- Structural checks do not prove every transcribed source value is correct.
- Population provenance is documented, but the original PDF is not bundled and each cell has not been independently visually audited in this run.
- The Ladakh corrections are supported by cited official PIB/MHA tables, but the team should retain the links and recheck them before publication.
- The 2018–2019 boundary caveat remains a methodological limitation.

## 8. Reproduction
From the submission root, run:

```bash
python scripts/build_person2_dataset.py
```

The script regenerates the three canonical datasets and audit CSVs. A second run should produce the same outputs when inputs and software versions remain unchanged.
