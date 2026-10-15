# Source download register

The original PDFs could not be saved into this repository: the workspace used to build it was blocked from Indian government hosts, and the NCRB site disallows automated access. Each document below was read online on **2026-10-08** and transcribed. Whoever downloads them should save them under `data/source_documents/` with the suggested file name, then tick the last column.

| source_id | Official link | Suggested file name | Publication date / version | Raw-data file(s) created | Downloaded? |
|---|---|---|---|---|---|
| S01 | https://www.mha.gov.in/MHA1/Par2017/pdfs/par2025-pdfs/LS02122025/438.pdf | `S01_LS_USQ438_2025-12-02.pdf` | Answered 02.12.2025 (Lok Sabha) | `data/raw/S01_LS_USQ438_2025-12-02_AnnexII_2014-2023.csv` | ☐ |
| S02 | https://www.mha.gov.in/MHA1/Par2017/pdfs/par2026-pdfs/LS17032026/4118.pdf | `S02_LS_USQ4118_2026-03-17.pdf` | Answered 17.03.2026 (Lok Sabha) | `data/raw/S02_LS_USQ4118_2026-03-17_Annex_2021-2023.csv` | ☐ |
| S03 | https://www.mha.gov.in/MHA1/Par2017/pdfs/par2025-pdfs/RS17122025/1998.pdf | `S03_RS_USQ1998_2025-12-17.pdf` | Answered 17.12.2025 (Rajya Sabha) | `data/raw/S03_RS_USQ1998_2025-12-17_Annex_2021-2023.csv` | ☐ |
| S04 | https://www.mha.gov.in/MHA1/Par2017/pdfs/par2024-pdfs/RS24072024/239.pdf | `S04_RS_USQ239_2024-07-24.pdf` | Answered 24.07.2024 (Rajya Sabha) | `data/raw/S04_RS_USQ239_2024-07-24_Annex_2018-2022.csv` | ☐ |
| S05 | https://www.mha.gov.in/MHA1/Par2017/pdfs/par2024-pdfs/RS27112024/234.pdf | `S05_RS_USQ234_2024-11-27.pdf` | Answered 27.11.2024 (Rajya Sabha) | `data/raw/S05a_..._AnnexI_2018-2022.csv`, `data/raw/S05b_..._AnnexII_fraud_CR_2018-2022.csv` | ☐ |
| S06 | https://eparlib.nic.in/bitstream/123456789/2971041/1/AU1432.pdf | `S06_LS_USQ1432_2023-12-12.pdf` | Answered 12.12.2023 (Lok Sabha) | `data/raw/S06_LS_USQ1432_2023-12-12_AnnexI_2020-2022.csv` | ☐ |
| S07 | https://eparlib.nic.in/bitstream/123456789/1930314/1/AU3307.pdf | `S07_LS_USQ3307_2023-03-21.pdf` | Answered 21.03.2023 (Lok Sabha) | `data/raw/S07_LS_USQ3307_2023-03-21_AnnexI_2019-2021.csv` | ☐ |
| S08 | https://eparlib.nic.in/bitstream/123456789/951400/1/AU1738.pdf | `S08_LS_USQ1738_2019-07-02.pdf` | Answered 02.07.2019 (Lok Sabha) | `data/raw/S08_LS_USQ1738_2019-07-02_AnnexI_2014-2016.csv` | ☐ |
| S09 | https://static.pib.gov.in/WriteReadData/specificdocs/documents/2025/mar/doc2025318522301.pdf | `S09_PIB_doc2025318522301.pdf` | Hosted March 2025; parent release not identified | `data/raw/S09a_..._AnnexI_2020-2022.csv`, `data/raw/S09b_..._AnnexII_fraud_2020-2022.csv` | ☐ |
| S10 | https://www.data.gov.in/resource/stateut-wise-number-cases-registered-under-cyber-crimes-2018-2022 | `S10_datagovin_cyber_2018-2022.csv` | Published/updated 09.09.2024 | none (duplicate of S04; download to confirm) | ☐ |
| S11 | https://eparlib.sansad.in/bitstream/123456789/956307/1/AU587.pdf | `S11_LS_USQ587_2019-06-25.pdf` | Answered 25.06.2019 | none (reviewed only) | ☐ |
| S12 | https://www.mha.gov.in/MHA1/Par2017/pdfs/par2021-pdfs/rs-08122021/1164.pdf | `S12_RS_USQ1164_2021-12-08.pdf` | Answered 08.12.2021 | none (national only) | ☐ |
| S13 | https://www.mha.gov.in/MHA1/Par2017/pdfs/par2021-pdfs/LS-03082021/2348.pdf | `S13_LS_USQ2348_2021-08-03.pdf` | Answered 03.08.2021 | none (national only) | ☐ |
| S14 | Official PDF not located (mirror: https://www.datais.info/loksabha/question/97b414cb67337ef47a4dd49117430002/Cyber+Crime/) | `S14_LS_USQ2895_2020-03-11.pdf` | Answered 11.03.2020 (MeitY) | none (context only) | ☐ |
| S15 | https://eparlib.nic.in/bitstream/123456789/589198/1/93002.pdf | `S15_LS_SQ336_2010-08-17.pdf` | Answered 17.08.2010 | none (not comparable) | ☐ |
| S16 | https://www.ncrb.gov.in/crime-in-india-year-wise.html | `S16_NCRB_CII_<year>_Vol1.pdf` for 2016, 2019, 2022, 2023 | Annual; 2023 edition released Sept 2025 | none yet - **verification target for S01** | ☐ |

Notes
- NCRB PDFs are large (Volume 1 runs to several hundred pages). If they are too big for GitHub, keep them out of the repository and record the file's SHA-256 here instead.
- Parliamentary PDFs are small (a few pages) and can go in the repository.
- `data/source_documents/extraction_transcripts/` contains the text transcribed from each table; those are what the raw CSVs are built from.
