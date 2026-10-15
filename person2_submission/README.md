# Person 2 Submission — Cybercrime Data Preparation

## Purpose
This folder contains Person 2's reproducible data-cleaning and feature-engineering work for State/UT-level **registered total cybercrime cases** in India. The analysis window is 2018–2023. It is designed to be understandable without reading the code first.

## Start here
1. Read `docs/person2_handover_summary.md` for the project scope and deliverables.
2. Read `docs/data_cleaning_log.md` for every important cleaning and boundary decision.
3. Read `docs/population_source_notes.md` before interpreting population-adjusted rates.
4. Use `docs/data_dictionary.md` to understand columns in each output.
5. Read `docs/processed_data_validation.md` for checks and known limitations.

## Folder map
```text
person2_submission/
├── README.md
├── data/
│   ├── source_inputs/                 # Only the two Person 1 inputs required to rebuild
│   │   ├── S01_LS_USQ438_2025-12-02_AnnexII_2014-2023.csv
│   │   └── state_ut_naming_reference.csv
│   ├── external/
│   │   └── population_source_values.csv  # Extracted values with official source provenance
│   ├── reference/
│   │   └── ladakh_correction_log.csv     # Person 2's documented external corrections
│   └── processed/
│       ├── cybercrime_master_2018_2023.csv
│       ├── cybercrime_model_input.csv
│       ├── cybercrime_model_features.csv
│       └── audit/
│           ├── input_inventory.csv
│           ├── ladakh_correction_log.csv
│           ├── national_total_reconciliation.csv
│           └── validation_checks.csv
├── docs/                              # Exactly five explanatory Markdown documents
└── scripts/
    └── build_person2_dataset.py       # The one canonical pipeline script
```

## Which Person 1 files are included?
Only these two inputs are included because the script requires them:
- the primary S01 State/UT cybercrime series; and
- the S01 State/UT naming reference.

Other Person 1 files, transcripts, helper scripts, and raw evidence packages are **not** copied into this submission. The two included source inputs are treated as read-only. Population values and the Ladakh correction log are separate inputs documented for Person 2's processing.

## Outputs
- `cybercrime_master_2018_2023.csv`: full traceable dataset with source fields, cleaned case count, population, derived features, and quality/boundary flags.
- `cybercrime_model_input.csv`: compact analytical table for descriptive statistics and visualisation.
- `cybercrime_model_features.csv`: target-separated table for later forecasting/model training. Do not use `target_reported_cases` or `target_missing` as predictors.
- `processed/audit/`: input inventory, correction evidence, annual reconciliation, and machine-readable validation checks.

## Rebuild the outputs
Run from this folder with Python 3 and `pandas` and `numpy` installed:

```bash
python scripts/build_person2_dataset.py
```

The script reads only the inputs listed above and overwrites the three canonical output CSVs and audit CSVs. It does not modify source inputs. After running, compare the console checks with `docs/processed_data_validation.md`.

## Scope and interpretation
- One row per State/UT-year, 36 entities × 6 years = 216 rows.
- Only State/UT records for the total cybercrime measure are selected; all-India/aggregate rows and fraud-only records are excluded.
- Missing values are never replaced with zero.
- Ladakh values for 2020–2023 are applied from cited official corroborating tables; 2018–2019 remain unresolved.
- The 2019 territorial reorganisation creates a comparability break for historical Jammu & Kashmir/Ladakh records. See the cleaning log and validation report.
- Population figures are official projections, not observed census counts. Rates are therefore estimates and are suppressed where the territorial denominator is not comparable.
