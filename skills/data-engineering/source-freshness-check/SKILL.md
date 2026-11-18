---
name: source-freshness-check
description: >-
  Compares the newest timestamp in an export to warn and error ages the user
  sets. Use when the user asks whether a source or a model is fresh enough,
  without querying the warehouse.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/check_freshness.py. No network and no extra
  packages.
metadata:
  category: data-engineering
  subshelf: warehouses
  tags: freshness, dbt
  added: "2026-11-17"
  featured: false
---

# Source freshness check

Judge one export against ages the user set. Do not query a warehouse, and do not invent an SLA. A scan-cost reading of SQL stays with warehouse-scan-review.

## Steps

1. Confirm the file, the timestamp column, the as-of time, and at least one threshold. Each threshold is a positive count plus a period of `minute`, `hour`, or `day`. When the as-of time or a number is missing, ask. Do not read the wall clock.
2. Run `python3 scripts/check_freshness.py` on that file. The fixture is [assets/sample.csv](assets/sample.csv), and it is not a live table. A date with no clock time is midnight UTC.
3. Report `rows`, `nonempty`, `blank`, `max_loaded_at`, `as_of`, `age_seconds`, the thresholds, and `status` as printed.
4. The script sets `warn` when the age is greater than the warn threshold, and `error` when the age is greater than the error threshold. An equal age stays at the milder status. That comparison is the script's rule for this file.
5. When the script rejects the file, the column, a timestamp, or a threshold, stop and quote the message. Do not guess a time.
6. Check that the as-of time and the thresholds are the ones the user supplied. A pass is not a claim that dbt ran.

## Example

User: Check `assets/sample.csv`, column `loaded_at`, as of `2026-11-17T12:00:00Z`. Warn after 12 hours. Error after 24 hours. Do not query the warehouse.

Agent: Runs `python3 scripts/check_freshness.py assets/sample.csv --column loaded_at --as-of 2026-11-17T12:00:00Z --warn-count 12 --warn-period hour --error-count 24 --error-period hour`. The script prints `nonempty=2`, `blank=1`, `max_loaded_at=2026-11-16T18:00:00Z`, `age_seconds=64800`, `warn_after=12h`, `error_after=24h`, and `status=warn`. The blank `loaded_at` is skipped. No warehouse is queried.

## Boundaries

This reads a file the user already has. It does not run `dbt freshness`, page anyone, or treat the fixture as production data. `status=warn` is about this file and this as-of time only.

## References

dbt freshness is a count plus a period of minute, hour, or day, on `warn_after` and `error_after`, compared with the newest `loaded_at_field`. The vocabulary is documented at [freshness](https://docs.getdbt.com/reference/resource-configs/freshness). The command that evaluates it is [`dbt freshness`](https://docs.getdbt.com/reference/commands/freshness). This skill borrows those two thresholds for an export. It does not render dbt's query.
