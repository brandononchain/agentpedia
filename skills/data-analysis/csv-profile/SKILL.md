---
name: csv-profile
description: >-
  Profiles a CSV file with row counts, empty cells, distinct values, and sample
  values per column. Use when the user asks what is in a spreadsheet export or a
  CSV before any analysis.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/profile_csv.py. No network and no extra
  packages.
metadata:
  category: data-analysis
  subshelf: profiles
  tags: csv, data
  added: "2026-11-07"
  featured: false
---

# CSV profile

Profile a CSV before drawing conclusions from it. Use the bundled script instead of guessing column types. A profile is a description of the file, not an analysis of why the numbers look that way.

## Steps

1. Confirm the file path and that the user wants a profile, not a chart or a model.
2. Run `python3 scripts/profile_csv.py` on that file. For a dry run of the script, use [assets/sample.csv](assets/sample.csv).
3. Report rows, columns, and for each column the empty count, the distinct count, and the sample values the script printed.
4. Call out columns that are entirely empty, columns with a single distinct value, and columns whose samples mix formats (dates beside free text).
5. Validate the report against the script output. Do not add totals, averages, or causes that the script did not compute.

## Example

User: Profile `assets/sample.csv` in this skill folder.

Agent: Runs the script and reports 3 data rows and 4 columns. `pnl` has 1 empty cell. `symbol` has 2 distinct values, sample `EURUSD` and `XAUUSD`. No averages are added.

## Boundaries

Do not upload the file anywhere. Do not treat a sample value as a typical value. Say when the file is empty.
