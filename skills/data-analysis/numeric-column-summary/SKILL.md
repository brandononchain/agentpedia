---
name: numeric-column-summary
description: >-
  Summarizes one numeric CSV column with count, min, max, mean, and nearest-rank
  quartiles. Use when the user asks for the distribution of a column in a file
  they already have.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/summarize_column.py. No network and no extra
  packages.
metadata:
  category: data-analysis
  subshelf: profiles
  tags: csv, distribution
  added: "2026-11-16"
  featured: false
---

# Numeric column summary

Report the distribution of one column from a CSV the user already has. Every figure comes from `scripts/summarize_column.py`. A profile of empty cells and distinct values, without min or mean, belongs to csv-profile.

## Steps

1. Confirm the file and the column name. If the user did not name a column, ask instead of picking one.
2. Run `python3 scripts/summarize_column.py` on that file with `--column` set to the name they gave. The sample is [assets/sample.csv](assets/sample.csv).
3. Copy the printed lines: row count, numeric count, blanks, non-numeric cells, min, p25, median, p75, max, sum, and mean.
4. If the script prints `percentiles=not-computed`, say the column has no numeric values. Do not substitute a zero.
5. Check that min, max, and the quartiles are values from the numeric rows, and that mean is the printed sum divided by the numeric count. The rank rule is in [references/nearest-rank.md](references/nearest-rank.md).

## Example

User: Summarize `latency_ms` in `assets/sample.csv`.

Agent: Runs the script. rows=6, numeric=4, blank=1, non_numeric=1 (`n/a`). min=80, p25=80, median=100, p75=120, max=200, sum=500, mean=125. The blank row stays blank. 500 divided by 4 is 125.

## Boundaries

Do not strip a thousands separator, do not drop non-numeric rows to tidy the mean, and do not call a quartile a confidence interval. This is a description of one column, not a forecast.

## References

Typed totals are out of bounds for the same reason the xlsx skill in [anthropics/skills](https://github.com/anthropics/skills/blob/main/skills/xlsx/SKILL.md) requires spreadsheet results to come from formulas. This script is stdlib-only. It does not call the dataset `/statistics` route described in [huggingface/skills](https://github.com/huggingface/skills/blob/main/skills/huggingface-datasets/SKILL.md).
