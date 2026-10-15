"""Build raw CSVs from the extraction transcripts.

Reads every data/source_documents/extraction_transcripts/*.txt file and writes:
  data/raw/<transcript_stem>.csv             one file per source table
  data/raw/cybercrime_raw_all_sources.csv    all rows stacked (incl. total rows)
  docs/validation_sum_checks.csv             state/UT sums vs printed totals
  docs/cross_source_comparison.csv           same state-year across sources

No value is altered. reported_cases_raw is filled only when raw_value_text is
a plain integer (commas removed); otherwise it is left empty.

Run from the repository root:  python scripts/build_raw.py
"""
import csv
import glob
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TDIR = os.path.join(ROOT, "data", "source_documents", "extraction_transcripts")
RAW = os.path.join(ROOT, "data", "raw")
DOCS = os.path.join(ROOT, "docs")

# Per-source descriptive fields (kept here so every row is self-describing)
SOURCES = {
    "S01": dict(source_name="NCRB 'Crime in India' via MHA reply, Lok Sabha USQ 438 (02.12.2025)",
                table_page="Annexure-II 'State/UT-wise Cases Registered under Cyber Crimes during 2014-2023'; annexure page header 'L.S. US.Q. NO. 438 FOR 02.12.2025'; no printed page no."),
    "S02": dict(source_name="NCRB 'Crime in India' via MHA reply, Lok Sabha USQ 4118 (17.03.2026)",
                table_page="Annexure 'State/UT-wise Cases Registered under Cyber Crimes during 2021-2023'; no printed page no."),
    "S03": dict(source_name="NCRB 'Crime in India' via MHA reply, Rajya Sabha USQ 1998 (17.12.2025)",
                table_page="Annexure 'State/UT-wise Cases Registered under Cyber Crimes during 2021-2023'; no printed page no."),
    "S04": dict(source_name="NCRB 'Crime in India' via MHA reply, Rajya Sabha USQ 239 (24.07.2024)",
                table_page="Annexure 'STATE/UT-WISE CASES REGISTERED UNDER CYBER CRIMES DURING 2018-2022'; no printed page no."),
    "S05": dict(source_name="NCRB 'Crime in India' via MHA reply, Rajya Sabha USQ 234 (27.11.2024)",
                table_page=None),  # set per file below
    "S06": dict(source_name="NCRB 'Crime in India' via MHA reply, Lok Sabha USQ 1432 (12.12.2023)",
                table_page="ANNEXURE-I 'STATE/UT-WISE CASES REGISTEREDUNDER CYBER CRIMES DURING 2020-2022' (header 'LSQ.NO. 1432 FOR 12.12.2023')"),
    "S07": dict(source_name="NCRB 'Crime in India' via MHA reply, Lok Sabha USQ 3307 (21.03.2023)",
                table_page="Annexure-I (state/UT-wise CR, CCS, CON, PAR, PCS, PCV 2019-2021); CR columns only; exact printed title not captured"),
    "S08": dict(source_name="NCRB 'Crime in India' via MHA reply, Lok Sabha USQ 1738 (02.07.2019)",
                table_page="Annexure-I (state/UT-wise cyber crime cases 2014-2016); exact printed title not captured"),
    "S09": dict(source_name="NCRB 'Crime in India' via PIB-hosted document doc2025318522301 (Mar 2025)",
                table_page=None),
}
FILE_TABLE = {
    "S05a": "Annexure-I 'STATE/UT-WISE CASES REGISTERED UNDER CYBER CRIMES DURING 2018-2022'",
    "S05b": "Annexure-II pages 1-2 (state-wise CR/CCS/CON/PAR/PCS/PCV under fraud for cyber crimes 2018-2022); CR columns only; exact printed title paraphrased by tool",
    "S09a": "Annexure-I 'State/UT-wise Cases Registered (CR) under Cyber Crimes during 2020-2022'",
    "S09b": "Annexure-II 'State/UT-wise Cases Registered (CR) under Fraud for Cyber Crimes during Year 2020-2022'",
}

FOOTNOTES = {
    "+": "'+' = combined data of erstwhile D&N Haveli UT and Daman & Diu UT for 2018, 2019 (per source footnote)",
    "*": "'*' = data of erstwhile Jammu & Kashmir State including Ladakh for 2018, 2019 (per source footnote)",
    "#": "'#' = clarifications pending from Nagaland for the year 2022 (per source footnote)",
}

# Row-level observations (source_prefix, name_contains, year) -> note
ROW_NOTES = [
    ("S01", "Ladakh", None, "Source row prints only four values (1, 5, 3, 1) for ten year columns; year alignment could not be confirmed from the text layer, so cell left blank. Sum check: S01 TOTAL UT(S) minus the other seven UTs leaves exactly 1/5/3/1 for 2020/2021/2022/2023 and 0 for 2014-2019, matching S02-S07 - consistent with Ladakh '-' for 2014-2019; verify visually in PDF."),
    ("S01", "Jammu & Kashmir", 2014, "Placed in UT block for all years; for 2014-2019 this is the erstwhile J&K State (incl. Ladakh; reorganised 31.10.2019). S01 TOTAL STATE(S) for 2014-2017 excludes J&K, unlike S08 (9285 vs 9322 in 2014)."),
    ("S01", "Jammu & Kashmir", 2015, "Erstwhile J&K State (incl. Ladakh) counted in UT block - see 2014 note."),
    ("S01", "Jammu & Kashmir", 2016, "Erstwhile J&K State (incl. Ladakh) counted in UT block - see 2014 note."),
    ("S01", "Jammu & Kashmir", 2017, "Erstwhile J&K State (incl. Ladakh) counted in UT block - see 2014 note."),
    ("S01", "Jammu & Kashmir", 2018, "Erstwhile J&K State incl. Ladakh (S04 footnote). Value 73 identical to 2019 - verify against Crime in India 2019 Table 9A.1 footnotes."),
    ("S01", "Jammu & Kashmir", 2019, "Erstwhile J&K State incl. Ladakh (S04 footnote; reorganisation effective 31.10.2019)."),
    ("S01", "D&N Haveli and Daman & Diu", 2014, "Combined retroactively; S08 prints D&N Haveli=3, Daman & Diu=1 separately."),
    ("S01", "D&N Haveli and Daman & Diu", 2015, "Combined retroactively; S08 prints D&N Haveli=0, Daman & Diu=1."),
    ("S01", "D&N Haveli and Daman & Diu", 2016, "Combined retroactively; S08 prints D&N Haveli=1, Daman & Diu=0."),
    ("S01", "D&N Haveli and Daman & Diu", 2017, "Combined retroactively (UTs merged 26.01.2020)."),
    ("S01", "D&N Haveli and Daman & Diu", 2018, "Combined retroactively (UTs merged 26.01.2020)."),
    ("S01", "D&N Haveli and Daman & Diu", 2019, "Combined retroactively (UTs merged 26.01.2020)."),
    ("S01", "Lakshadweep", 2018, "Value 4 identical to 2019 - verify against Crime in India 2019."),
    ("S01", "Andhra Pradesh", 2023, "Value 2341 identical to 2022 in S01, S02 and S03 - verify against Crime in India 2023 Table 9A.1."),
    ("S02", "Andhra Pradesh", 2023, "Value 2341 identical to 2022 - verify against Crime in India 2023."),
    ("S03", "Andhra Pradesh", 2023, "Value 2341 identical to 2022 - verify against Crime in India 2023."),
    ("S01", "Nagaland", 2022, "S06 footnote: clarifications pending from Nagaland for 2022."),
    ("S01", "Telangana", 2014, "Telangana formed 02.06.2014; check Crime in India 2014 for how pre-formation cases were split with Andhra Pradesh."),
    ("S08", "Telangana", 2014, "Telangana formed 02.06.2014; check Crime in India 2014 for split with Andhra Pradesh."),
    ("S08", "Jammu & Kashmir", None, "Listed as a STATE (pre-2019 boundaries) and counted in TOTAL STATE(S)."),
    ("S05b", "D&N Haveli and Daman & Diu", 2018, "Fraud-category CR only; not total cyber crime."),
]

INT_RE = re.compile(r"^-?\d{1,3}(,\d{3})*$|^-?\d+$")


def parse(path):
    meta, cols, rows = {}, None, []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        if line.startswith("#"):
            k, _, v = line[1:].partition(":")
            meta.setdefault(k.strip(), []).append(v.strip())
            continue
        if line.startswith("COLUMNS:"):
            cols = line[len("COLUMNS:"):].strip().split("|")
            continue
        cells = line.split("|")
        if len(cells) != len(cols):
            raise ValueError(f"{os.path.basename(path)}: column count mismatch in line: {line}")
        rows.append(cells)
    return meta, cols, rows


def row_type(sl, name):
    u = name.upper()
    if "TOTAL (ALL INDIA)" in u:
        return "total_all_india"
    if "TOTAL STATE" in u:
        return "total_states"
    if "TOTAL UT" in u:
        return "total_uts"
    return "state_ut"


def main():
    os.makedirs(RAW, exist_ok=True)
    fields = ["source_id", "source_table_key", "state_ut_original", "sl_no_original", "row_type", "block",
              "year", "reported_cases_raw", "raw_value_text", "measure_type", "category",
              "source_name", "source_file", "table_page", "source_url", "notes"]
    all_rows = []
    for path in sorted(glob.glob(os.path.join(TDIR, "*.txt"))):
        stem = os.path.splitext(os.path.basename(path))[0]
        key = stem.split("_")[0]          # e.g. S05b
        sid = re.match(r"S\d+", key).group(0)
        meta, cols, rows = parse(path)
        years = [int(c) for c in cols[2:]]
        is_fraud = "fraud" in stem.lower()
        measure = "registered cases (CR)"
        category = ("Cyber crimes - Fraud (sub-category; NOT total cyber crime)" if is_fraud
                    else "Total cyber crimes (IT Act + IPC + SLL, NCRB definition)")
        table_page = FILE_TABLE.get(key) or SOURCES[sid]["table_page"]
        url = meta.get("url", [""])[0]
        out = []
        block = "states"
        for cells in rows:
            sl, name = cells[0], cells[1]
            rt = row_type(sl, name)
            if rt == "total_states":
                block_here = "states"
            elif rt in ("total_uts", "total_all_india"):
                block_here = "uts" if rt == "total_uts" else "all_india"
            else:
                block_here = block
            for y, txt in zip(years, cells[2:]):
                raw = txt.replace(",", "") if INT_RE.match(txt.strip()) else ""
                notes = []
                if txt.strip() == "":
                    notes.append("Blank cell in extracted text.")
                elif txt.strip() == "-":
                    notes.append("Dash printed in source (not zero); entity did not exist separately in this year.")
                for sym, expl in FOOTNOTES.items():
                    if sym in name and sym in " ".join(sum(meta.values(), [])) :
                        if sym in ("+", "*") and y not in (2018, 2019):
                            continue
                        if sym == "#" and y != 2022:
                            continue
                        notes.append(expl)
                for pref, nm, yr, note in ROW_NOTES:
                    if key.startswith(pref) and (key == pref or len(pref) == 3) and nm in name and (yr is None or yr == y):
                        notes.append(note)
                out.append(dict(source_id=sid, source_table_key=key, state_ut_original=name,
                                sl_no_original=sl, row_type=rt, block=block_here, year=y,
                                reported_cases_raw=raw, raw_value_text=txt, measure_type=measure,
                                category=category, source_name=SOURCES[sid]["source_name"],
                                source_file=os.path.basename(path), table_page=table_page,
                                source_url=url, notes=" | ".join(dict.fromkeys(notes))))
            if rt == "total_states":
                block = "uts"
        with open(os.path.join(RAW, stem + ".csv"), "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(out)
        all_rows.extend(out)

    with open(os.path.join(RAW, "cybercrime_raw_all_sources.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(all_rows)

    # ---- sum checks: states block vs TOTAL STATE(S), UT block vs TOTAL UT(S), both vs ALL INDIA
    checks = []
    by = defaultdict(list)
    for r in all_rows:
        by[(r["source_table_key"], r["year"])].append(r)
    for (key, y), rs in sorted(by.items()):
        def tot(rt):
            v = [r for r in rs if r["row_type"] == rt]
            return int(v[0]["reported_cases_raw"]) if v and v[0]["reported_cases_raw"] else None
        st = [r for r in rs if r["row_type"] == "state_ut" and r["block"] == "states"]
        ut = [r for r in rs if r["row_type"] == "state_ut" and r["block"] == "uts"]
        blanks = [r["state_ut_original"] for r in st + ut if r["reported_cases_raw"] == ""]
        s_sum = sum(int(r["reported_cases_raw"]) for r in st if r["reported_cases_raw"])
        u_sum = sum(int(r["reported_cases_raw"]) for r in ut if r["reported_cases_raw"])
        ts, tu, ta = tot("total_states"), tot("total_uts"), tot("total_all_india")
        checks.append(dict(source_table_key=key, year=y,
                           n_state_rows=len(st), n_ut_rows=len(ut),
                           sum_states=s_sum, printed_total_states=ts, states_match=(s_sum == ts),
                           sum_uts=u_sum, printed_total_uts=tu, uts_match=(u_sum == tu),
                           printed_all_india=ta, states_plus_uts_match_all_india=(ts is not None and tu is not None and ts + tu == ta),
                           sum_all_rows=s_sum + u_sum, rows_match_all_india=(s_sum + u_sum == ta),
                           non_numeric_cells="; ".join(blanks)))
    with open(os.path.join(DOCS, "validation_sum_checks.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(checks[0].keys()))
        w.writeheader()
        w.writerows(checks)

    # ---- cross-source comparison for total cyber crime tables
    norm = lambda s: re.sub(r"[\s\*\+#]+$", "", re.sub(r"\s+", " ", s)).replace("A & N", "A&N")
    norm2 = lambda s: re.sub(r" UT$", "", norm(s)).strip()
    grid = defaultdict(dict)
    for r in all_rows:
        if "Fraud" in r["category"]:
            continue
        grid[(norm2(r["state_ut_original"]), r["year"])][r["source_table_key"]] = r["raw_value_text"]
    keys = sorted({r["source_table_key"] for r in all_rows if "Fraud" not in r["category"]})
    comp = []
    for (name, y), d in sorted(grid.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        vals = {v for v in d.values() if v not in ("",)}
        row = dict(state_ut_normalised_for_matching=name, year=y)
        row.update({k: d.get(k, "") for k in keys})
        row["n_sources"] = len(d)
        row["all_sources_agree"] = len(vals) <= 1
        comp.append(row)
    with open(os.path.join(DOCS, "cross_source_comparison.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(comp[0].keys()))
        w.writeheader()
        w.writerows(comp)

    print(f"rows written: {len(all_rows)}")
    bad = [c for c in checks if not (c["states_match"] and c["uts_match"] and c["rows_match_all_india"])]
    print(f"sum-check failures: {len(bad)}")
    for c in bad:
        print("  ", c)
    dis = [c for c in comp if not c["all_sources_agree"]]
    print(f"cross-source disagreements: {len(dis)}")
    for c in dis:
        print("  ", c)


if __name__ == "__main__":
    main()
