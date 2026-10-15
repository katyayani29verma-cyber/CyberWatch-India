# State/UT-wise cybercrime in India — raw evidence base

Raw data, source documentation and checks for a state/UT-level analysis of cybercrime in India, built from NCRB *Crime in India* figures as reproduced in Ministry of Home Affairs parliamentary replies and a PIB document. Prepared 2026-10-08. Nothing in `data/raw/` has been cleaned or corrected.

## Folders and files

```
README.md
scripts/build_raw.py                      transcripts -> raw CSVs + validation files (python 3, stdlib only)
data/
  raw/
    cybercrime_raw_all_sources.csv        all rows from all source tables (one row = one State/UT or total row, one year, one source)
    S01_..._2014-2023.csv ... S09b_...    one CSV per source table
  source_documents/
    README.md                             why the PDFs are not here
    extraction_transcripts/*.txt          the text transcribed from each table, with metadata header
  external/README.md                      population data: not collected (guidance)
docs/
  source_inventory.csv                    every source used or reviewed (S01-S18) with comparability status
  extraction_log.md                       how each table was extracted, blanks, dashes, footnotes, sum checks
  source_download_register.md            official links and file names for every source document
  state_ut_naming_reference.csv           source-specific names -> suggested standard names
  data_collection_summary.md             years, primary source, comparability, limitations, next checks
  validation_sum_checks.csv               State/UT sums vs printed totals for each table-year
  cross_source_comparison.csv             same State/UT-year side by side across sources
```

Raw CSV columns: `source_id`, `source_table_key`, `state_ut_original`, `sl_no_original`, `row_type`, `block`, `year`, `reported_cases_raw`, `raw_value_text`, `measure_type`, `category`, `source_name`, `source_file`, `table_page`, `source_url`, `notes`. `source_id` links each row to `docs/source_inventory.csv`.

To rebuild: `python scripts/build_raw.py` from the repository root.

## Where Person 2 should start

1. **`data/raw/S01_LS_USQ438_2025-12-02_AnnexII_2014-2023.csv`** — the primary series (total cyber crime, registered cases, 2014–2023, 36 States/UTs).
2. Main analysis window: **2018–2023**. 2017 is usable with caution; 2014–2016 for context only. Reasons in `docs/data_collection_summary.md`.
3. Filter `row_type == "state_ut"` to drop total rows; filter `category` to keep total cyber crime and exclude the Fraud tables (S05b, S09b).
4. Use `docs/state_ut_naming_reference.csv` to map names; keep `state_ut_original` untouched.

## Known issues needing attention

- Original PDFs not in the repo; values were read from PDF text layers and are **not yet visually verified**. All sum checks and cross-source comparisons pass (`docs/validation_sum_checks.csv`, `docs/cross_source_comparison.csv`).
- S01 Ladakh cells are blank (four values printed without clear year alignment). Sum checks imply 2020–2023 = 1, 5, 3, 1.
- 2017 has only one source (S01).
- J&K 2018–2019 include Ladakh; J&K and Lakshadweep have identical 2018 and 2019 values; Andhra Pradesh 2022 = 2023 = 2,341. Verify against NCRB.
- NCRB revised all-India 2019 from 44,546 to 44,735 between editions.
- Nagaland 2022: clarifications pending (NCRB footnote).
- No population data yet.
