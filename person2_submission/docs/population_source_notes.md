# Population Source Notes

## Source and interpretation
- **Document:** *Population Projections for India and States 2011–2036*.
- **Issuing authority:** Ministry of Health and Family Welfare, Government of India.
- **Table:** Table 14, “Projected Total Population by Sex as on 1st October — 2011–2036: India, States and Union Territories”.
- **Measure used:** Persons.
- **Original unit:** Thousands.
- **Years used:** 2018–2023.
- **Official source URL:** https://www.mohfw.gov.in/sites/default/files/Population%20Projection%20Report%202011-2036%20-%20upload_compressed_0.pdf

## What the included file is
`data/external/population_source_values.csv` is a structured extraction of the relevant Table 14 values, not the original PDF and not an untouched raw source document. Each row retains a source identifier, URL and table reference so that the values can be traced back to the official publication. The PDF itself is not bundled in this Person 2 submission.

## Processing and boundary harmonisation
- `population_thousands` stores the values in the table's original unit.
- `population_persons` is calculated as `population_thousands × 1,000`.
- State/UT names are mapped to the same standard names used by the cybercrime panel.
- Dadra & Nagar Haveli and Daman & Diu are represented as the unified current Union Territory in the 36-entity panel; the historical boundary implications should be considered for analyses of earlier years.
- The extracted panel has 216 State/UT-year rows and unique keys.

## Limitations
These are projections, not observed census counts, and values in the source are rounded to the nearest thousand. Crime rates therefore inherit projection uncertainty. Population figures on current boundaries do not make pre-reorganisation Jammu & Kashmir/Ladakh case counts directly comparable to the post-reorganisation series. For that reason, the pipeline suppresses historical rates where the denominator is incompatible and flags the relevant records.

Before publication, a team member should manually compare the extracted values with the official PDF. This submission documents provenance and transformation but does not claim independent visual verification of every population cell.
