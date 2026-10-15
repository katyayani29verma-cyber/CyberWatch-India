# Extraction log

Prepared 2026-10-08. One section per source table. Every number in `data/raw/` comes from one of the transcripts in `data/source_documents/extraction_transcripts/`, and `scripts/build_raw.py` converts those transcripts to CSV without changing any value.

## 1. How extraction was done (applies to every source)

**Access constraint.** The cloud workspace used for this work cannot download files from Indian government hosts (`ncrb.gov.in`, `mha.gov.in`, `eparlib.nic.in`, `pib.gov.in`, `data.gov.in` all refused by the network allowlist). The NCRB website additionally disallows automated fetching in `robots.txt`. The original PDFs are therefore **not** in `data/source_documents/`; `docs/source_download_register.md` lists each one so the team can download it.

**Method.** Each PDF was read through a web-fetch tool that converts the PDF's embedded text layer to text and returns it. The tool was asked to return the table title, column headers, every row (name as printed, values as printed, including dashes and footnote symbols), total rows, footnotes and the source line. The returned rows were copied into a pipe-separated transcript file, one per table, with a metadata header. No OCR was involved; all documents had a text layer.

**What this means for reliability.**
- Values have **not** been checked visually against the rendered PDF pages. The checks that were done instead are (a) every state/UT column sums to the printed totals, and (b) the same state/UT-year appears in up to eight separate documents and was compared across them (section 4). Both checks passed, apart from the Ladakh row in S01 explained below.
- `raw_value_text` is the cell as it came out of the text layer. Thousands separators: none of the tables printed commas in their figures (e.g. `10741`, not `10,741`), so none appear. If the PDF typesets a value differently, the text layer may not show it.
- Printed page numbers: none of the parliamentary annexures carry printed page numbers. Table references therefore use annexure number and title; where an annexure has a running header (e.g. `L.S. US.Q. NO. 438 FOR 02.12.2025`) it is recorded.
- In three places the tool paraphrased or condensed a long title instead of returning it verbatim (S05b, S07, S08). These are flagged in the transcript header and in the inventory; the exact title must be copied from the PDF.
- Only the "Cases Registered (CR)" columns were transcribed from tables that also contain chargesheeting, conviction and arrest columns (S05b, S07).

**Conventions in the raw CSVs**
- `raw_value_text` = cell exactly as extracted; `reported_cases_raw` = the same value as an integer, filled only when the text is a plain number. A dash or blank stays empty in `reported_cases_raw`.
- `-` means the source printed a dash. In these tables it is used for Ladakh before 2020 (entity did not exist separately). It is **not** zero.
- Blank means the extraction returned no value for that cell (only the S01 Ladakh row).
- Footnote symbols are kept in `state_ut_original` exactly as printed (`Jammu & Kashmir *`, `D&N Haveli and Daman & Diu+`, `Nagaland #`), and the footnote meaning is written into `notes` for the years it applies to.
- `row_type` marks `state_ut`, `total_states`, `total_uts`, `total_all_india`. `block` records whether a row sits in the States block or the UTs block of the source table, which matters because J&K moves between blocks across sources.

## 2. Per-source extraction details

### S01 — Lok Sabha USQ 438, 02.12.2025 (MHA), Annexure-II, 2014–2023 — PRIMARY
- URL: https://www.mha.gov.in/MHA1/Par2017/pdfs/par2025-pdfs/LS02122025/438.pdf
- Table: Annexure-II "State/UT-wise Cases Registered under Cyber Crimes during 2014-2023". No printed page number; annexure pages carry the header "L.S. US.Q. NO. 438 FOR 02.12.2025". Annexure-I is a crime-head-wise national table (used only for the definition and for the IT Act / IPC / SLL subtotals below).
- Source line: "Source: 'Crime in India' published by NCRB." No footnotes printed.
- Layout: 28 States, then TOTAL STATE(S); 8 UTs, then TOTAL UT(S); TOTAL (ALL INDIA). Current boundaries are applied to every year: Jammu & Kashmir is in the UT block for all years and D&N Haveli and Daman & Diu is one row for all years.
- **Blank cells:** Ladakh, all ten years. The text layer printed four values (`1 5 3 1`) for ten year columns, so their position could not be determined from text alone. They were left blank rather than guessed. The UT sum check resolves the ambiguity: for 2020, 2021, 2022 and 2023 the printed TOTAL UT(S) exceeds the sum of the other seven UTs by exactly 1, 5, 3 and 1, and for 2014–2019 by 0. This matches Ladakh in S02–S07. A person looking at the PDF should confirm and fill the four cells in a later, documented step; the raw file stays blank.
- Dashes: none returned.
- Values worth a second look (printed this way, consistent across sources, but unusual):
  - Andhra Pradesh 2023 = 2341, the same as 2022. Also printed so in S02 and S03, and the 2023 state total (85603) only reconciles with this value. Check in Crime in India 2023.
  - Jammu & Kashmir 2018 = 2019 = 73, and Lakshadweep 2018 = 2019 = 4. Also so in S04, S05a, S07. Could indicate carried-forward data; check footnotes in Crime in India 2019.
  - Mizoram 2022 = 1, Manipur 2023 = 3, Assam 2021→2022 drop from 4846 to 1733: genuine-looking but large swings.
- Subtotal check from Annexure-I (national, crime-head-wise): IT Act + IPC + SLL = Total for every year, e.g. 2014: 7201 + 2272 + 149 = 9622; 2023: 44237 + 41849 + 334 = 86420.
- State totals vs official totals: States block sums to TOTAL STATE(S) for all 10 years. UT block sums to TOTAL UT(S) for 2014–2019; for 2020–2023 it falls short only by the Ladakh value (see above). TOTAL STATE(S) + TOTAL UT(S) = TOTAL (ALL INDIA) for all 10 years.

### S02 — Lok Sabha USQ 4118, 17.03.2026 (MHA), Annexure, 2021–2023
- URL: https://www.mha.gov.in/MHA1/Par2017/pdfs/par2026-pdfs/LS17032026/4118.pdf
- Table: "State/UT-wise Cases Registered under Cyber Crimes during 2021-2023". Question number printed as †4118 (in parliamentary papers the dagger usually marks a question received in Hindi; no effect on the data). No footnotes; no page number.
- Blanks/dashes: none. Sums: all match printed totals for all three years.

### S03 — Rajya Sabha USQ 1998, 17.12.2025 (MHA), Annexure, 2021–2023
- URL: https://www.mha.gov.in/MHA1/Par2017/pdfs/par2025-pdfs/RS17122025/1998.pdf
- Table: "State/UT-wise Cases Registered under Cyber Crimes during 2021-2023". No footnotes.
- Blanks/dashes: none. Sums: all match. Identical to S02 row for row.

### S04 — Rajya Sabha USQ 239, 24.07.2024 (MHA), Annexure, 2018–2022
- URL: https://www.mha.gov.in/MHA1/Par2017/pdfs/par2024-pdfs/RS24072024/239.pdf
- Table: "STATE/UT-WISE CASES REGISTERED UNDER CYBER CRIMES DURING 2018-2022".
- Footnotes (verbatim as extracted): "Note : '+' Combined data of erstwhile D&N Haveli UT and Daman & Diu UT for 2018, 2019"; "*' Data of erstwhile Jammu & Kashmir State including Ladakh for 2018, 2019". The stray quote marks are in the extracted text.
- Dashes: Ladakh 2018 and 2019 (`-`). Sums: all match for all five years.
- This is the table data.gov.in (S10) cites as its source.

### S05 — Rajya Sabha USQ 234, 27.11.2024 (MHA)
- URL: https://www.mha.gov.in/MHA1/Par2017/pdfs/par2024-pdfs/RS27112024/234.pdf
- **S05a, Annexure-I**, "STATE/UT-WISE CASES REGISTERED UNDER CYBER CRIMES DURING 2018-2022". Same footnotes as S04. Extraction issue: the text layer placed the 2018 value `0` of the "D&N Haveli and Daman & Diu+" row on a separate line; the tool aligned it as 0/3/3/5/5, which agrees with S04. Sums: all match.
- **S05b, Annexure-II (2 pages)**, state-wise cases registered, chargesheeted and convicted and persons arrested, chargesheeted and convicted under *fraud* for cyber crimes, 2018–2022. The printed title was paraphrased by the tool; copy it from the PDF. Only the CR column of each year was transcribed. Dashes: Ladakh 2018–2019. Footnotes: '+' and '*' as S04 (the '*' footnote text reads "during during", as printed). Sums: all match.
- Text-only figures in the answer (not tabulated): CFCFRMS "more than Rs. 3431 Crore" saved across "more than 9.94 lakh complaints". Recorded under S17, not in raw data.

### S06 — Lok Sabha USQ 1432, 12.12.2023 (MHA), Annexure-I, 2020–2022
- URL: https://eparlib.nic.in/bitstream/123456789/2971041/1/AU1432.pdf
- Table: "STATE/UT-WISE CASES REGISTEREDUNDER CYBER CRIMES DURING 2020-2022" (missing space as printed). Header "LSQ.NO. 1432 FOR 12.12.2023".
- Footnote: "# Clarifications are pending from Nagaland for the year 2022", attached to "Nagaland #".
- Annexure-II (cyber cells and cyber crime police stations, source BPR&D "Data on Police Organizations" 2022) was seen but not extracted; it is a police-infrastructure table, not crime data.
- Sums: all match.

### S07 — Lok Sabha USQ 3307, 21.03.2023 (MHA), Annexure-I, 2019–2021
- URL: https://eparlib.nic.in/bitstream/123456789/1930314/1/AU3307.pdf
- Annexure-I has, for each year, CR, cases chargesheeted, cases convicted, persons arrested, chargesheeted and convicted. Only CR transcribed. The tool condensed the printed title; copy it from the PDF.
- Dash: Ladakh 2019. Source line "Source: Crime in India". Tool reported no footnote symbols (S04 shows the same J&K/DNH figures with footnotes).
- First attempt to fetch this table was refused by the tool's quoting limit; a second request framed as numeric data extraction returned the rows.
- Sums: all match. All-India totals for persons (from the tool's summary): 2019–2021 arrested 15,268 / 18,420 / 27,374; not transcribed into raw data.

### S08 — Lok Sabha USQ 1738, 02.07.2019 (MHA), Annexure-I, 2014–2016
- URL: https://eparlib.nic.in/bitstream/123456789/951400/1/AU1738.pdf
- Pre-2019 layout: 29 States including Jammu & Kashmir; 7 UTs with "D&N Haveli" and "Daman & Diu" separate; "Delhi UT"; "A & N Islands".
- Title and source line were not captured by the tool. Copy from PDF.
- Sums: all match (TOTAL STATE(S) 9322 / 11331 / 12187; TOTAL UT(S) 300 / 261 / 130; All India 9622 / 11592 / 12317).
- Every individual state/UT value equals S01. The totals differ only because S01 moves J&K to the UT block (9322 − 37 = 9285) and S08 keeps DNH and DD separate (3 + 1 = 4 in 2014).

### S09 — PIB-hosted document doc2025318522301 (March 2025)
- URL: https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/mar/doc2025318522301.pdf
- The extracted text shows no ministry, date or question number. The parent PIB release was not identified; this should be found so the document can be cited properly.
- **S09a, Annexure-I**, "State/UT-wise Cases Registered (CR) under Cyber Crimes during 2020-2022". No '#' on Nagaland (S06 has it for the same numbers). Sums: all match.
- **S09b, Annexure-II**, "State/UT-wise Cases Registered (CR) under Fraud for Cyber Crimes during Year 2020-2022". Sums: all match. Identical to S05b for 2020–2022.

## 3. Sources reviewed but not extracted
See `docs/source_inventory.csv` rows S10–S18 for reasons. In short: S10 duplicates S04 and its table would not render; S11 is a six-page IPC-section fraud table (category-level, alignment caveats); S12–S14 are national-only; S15 is pre-2014 and uses a different definition; S16 (NCRB's own reports) could not be accessed; S17 counts complaints, not cases; S18 are unofficial compilations.

## 4. Results of automated checks
Generated by `scripts/build_raw.py`.

`docs/validation_sum_checks.csv` — 46 table-years checked. 42 pass every test. The 4 that do not are S01 2020–2023, where the UT block is short by exactly the blank Ladakh value; States + UTs = All-India still holds for those years.

`docs/cross_source_comparison.csv` — 366 state/UT-year cells (total-cyber-crime tables only). 318 cells appear in two or more documents (up to eight); **none disagree**. Cells with only one source: all 36 cells for **2017** (S01 is the only state-wise source found for 2017), plus the 2014–2016 rows whose names differ between S01 and S08 (combined vs separate D&N Haveli / Daman & Diu, and Ladakh).

The two fraud-category tables (S05b, S09b) agree with each other for 2020–2022.

## 5. Things a person with the PDFs should do
1. Open each PDF in the register and compare it with its transcript. Record the result in a new column or a short note.
2. Fill the S01 Ladakh cells only if the PDF shows their positions, and document the change.
3. Copy the exact titles for S05b, S07 and S08.
4. Download Crime in India 2019 (2017–2019) and Crime in India 2023 (2021–2023) and confirm 2017 values, J&K / Lakshadweep 2018–19, and Andhra Pradesh 2023.
