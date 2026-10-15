# data/source_documents

The original PDFs are **not** included: the environment used to build this package could not download from Indian government hosts, and the NCRB site disallows automated access. Download each file listed in `docs/source_download_register.md` and save it here under the suggested name.

`extraction_transcripts/` holds one text file per source table: a metadata header (source_id, document, URL, table title, footnotes, source line, extraction notes) followed by the rows exactly as extracted, pipe-separated. `scripts/build_raw.py` turns these into `data/raw/*.csv` without altering any value.
