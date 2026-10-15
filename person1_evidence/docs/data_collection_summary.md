# Data collection summary

Prepared 2026-10-08 for the state/UT cybercrime project.

## 1. What is available

| Years | State/UT-wise total cyber crime (registered cases) | Sources | Corroboration |
|---|---|---|---|
| 2014–2016 | Yes | S01, S08 | Every state/UT value identical in both |
| 2017 | Yes | S01 only | **Single source; not yet cross-checked** |
| 2018 | Yes | S01, S04, S05a | Identical |
| 2019 | Yes | S01, S04, S05a, S07 | Identical |
| 2020–2022 | Yes | S01, S04, S05a, S06, S07 (to 2021), S09a | Identical |
| 2023 | Yes | S01, S02, S03 | Identical |
| 2024 onward | Not yet published in any source found | — | — |
| Before 2014 | National totals only, different definition | S15 | Not comparable |

Also collected, but **not** a substitute for the above: state/UT-wise cases registered under the *Fraud* head of cyber crime, 2018–2022 (S05b; 2020–2022 also in S09b).

In total, 1,794 raw rows across 11 source tables, all in `data/raw/cybercrime_raw_all_sources.csv`.

## 2. Recommended primary source

**S01 — Lok Sabha Unstarred Question 438 (02.12.2025), Annexure-II**, which reproduces NCRB *Crime in India* figures for 2014–2023 in one table.

Why:
- One table, one definition, one publisher, ten years.
- It is the latest presentation of these figures, so it carries NCRB's revised values (see the 2019 point below).
- It already lays every year out on current boundaries (J&K in the UT block throughout; D&N Haveli and Daman & Diu combined throughout).
- All of its state/UT values for 2014–2016 and 2018–2023 match every other document that reports the same year.

The underlying authority is NCRB's *Crime in India* (S16). The NCRB reports themselves could not be accessed for this package, so S01 should be verified against them before publication (section 7).

## 3. Which years are comparable

**Main analysis: 2018–2023 (6 years × 36 States/UTs).**
Same NCRB crime-head list, current state/UT set, and every value confirmed by at least two independent documents. Two boundary points to handle explicitly:
- Jammu & Kashmir 2018–2019 are the erstwhile State *including* Ladakh; from 2020 J&K and Ladakh are separate. For a consistent J&K series, add Ladakh to J&K for 2020–2023 (or drop both from the panel).
- D&N Haveli and Daman & Diu is already combined for all years in S01/S04.

**Usable with caution: 2017.**
Expected to share the 2018-onward crime-head structure (S01 Annexure-I lists one head list for 2014–2023, and the extraction reported blank cells in several head rows, consistent with some heads not being collected in earlier years; which years are blank must be read from the PDF). The state values, however, come from one document only. Include in a sensitivity check, not the headline model, until verified against *Crime in India* 2019 (Table covering 2017–2019).

**Partially comparable: 2014–2016.**
Same broad definition (IT Act + IPC + SLL), and the numbers are corroborated, but NCRB's proforma had fewer crime heads before the 2017 edition (all-India 12,317 in 2016 vs 21,796 in 2017; part of that jump is likely classification, not crime). Use only for long-run descriptive context or robustness, and say so. The revision of proformae should be confirmed from the introduction of *Crime in India* 2017.

**Not comparable:**
- Anything before 2014 (IT Act and IPC reported separately, narrower set of sections, no SLL; S15).
- Fraud-category tables (S05b, S09b, S11): one crime head, not total cyber crime.
- NCRP / I4C complaint counts and amounts saved (S17): complaints, not registered cases.
- Future 2024+ data: the Bharatiya Nyaya Sanhita replaced the IPC from 1 July 2024, so the IPC part of the series will change heads. Treat 2024 as a new regime until NCRB documents a bridge.

## 4. What the data measures

- **Unit:** cases registered (FIRs) by police during the calendar year, counted in the State/UT where registered.
- **Scope of "cyber crime":** offences under the IT Act 2000, IPC sections where a computer or communication device is the medium or target (fraud, cheating, forgery, cyber stalking/bullying, defamation/morphing, fake profiles, data theft, blackmail, fake news and others), and Special & Local Laws (online gambling and lotteries, Copyright Act, Trade Marks Act, other SLL). National 2023: IT Act 44,237 + IPC 41,849 + SLL 334 = 86,420.
- It is **not**: complaints, victims, persons arrested, or money lost.

## 5. Important limitations

1. **Registered cases reflect policing as well as crime.** States with dedicated cyber police stations and easy online FIR registration (e.g. Karnataka, Telangana) report far more. A rise can mean more reporting or registration, not more crime.
2. **Revisions between editions.** All-India 2019 was 44,546 in *Crime in India* 2019 (S13) but 44,735 in later editions (S01, S04, S07). State values may also have been revised. Use one edition consistently and say which.
3. **Repeated or carried-forward values.** J&K (73) and Lakshadweep (4) are identical in 2018 and 2019; Andhra Pradesh is 2,341 in both 2022 and 2023. These are printed that way in every source but should be checked against NCRB footnotes.
4. **Pending clarifications.** Nagaland 2022 (S06 footnote). For 2018 an unofficial copy of a Lok Sabha answer (S14) reports clarifications pending from West Bengal, Assam, Arunachal Pradesh, Meghalaya and Sikkim.
5. **Small counts.** Many UTs and north-eastern states have single- or double-digit counts; percentage changes and rates for them are unstable.
6. **Boundaries.** Telangana created June 2014; J&K reorganised Oct 2019; DNH and Daman & Diu merged Jan 2020.
7. **Extraction method.** Values were read from PDF text layers, not checked visually against the page images (see `docs/extraction_log.md`). Automated sum and cross-source checks all pass, which makes transcription errors unlikely but does not replace a visual check.
8. **No population data yet.** Rates per lakh population cannot be computed from this package alone (section 6).

## 6. Population data

Not collected; `data/external/` is empty apart from a note. Recommendation: take the population figure NCRB itself uses for crime rates from the same *Crime in India* table (it reports mid-year projected population by State/UT). That keeps numerator and denominator consistent. NCRB's recent editions base these on the Technical Group on Population Projections (2011–2036) published by the National Commission on Population; confirm this from the report's notes. If collected, store it as `data/external/population_raw.csv` with its own source_id.

## 7. Remaining checks for Person 2

1. Download the PDFs in `docs/source_download_register.md`, especially S01 and NCRB *Crime in India* 2019 and 2023, and compare each transcript with the printed table.
2. Confirm the 2017 state values (only S01 so far).
3. Fill S01 Ladakh 2020–2023 only after seeing the PDF; the sum check implies 1, 5, 3, 1.
4. Check the J&K/Lakshadweep 2018 = 2019 and Andhra Pradesh 2022 = 2023 values and any related NCRB footnotes.
5. Record the exact titles for S05b, S07 and S08, and identify the parent PIB release for S09.
6. Decide and document how J&K/Ladakh will be handled across 2019→2020.
7. Decide which edition's values to use if NCRB originals differ from S01, and log every substitution in a separate cleaned dataset (never in `data/raw/`).
8. Add population and compute rates, if needed, from a documented source.
