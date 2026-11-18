---
name: series-gap-list
description: >-
  Lists missing timestamps in a regular series such as daily bars or hourly
  events. Use when the user asks which intervals are absent from a CSV they
  already have.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/list_gaps.py. No network and no extra
  packages.
metadata:
  category: data-analysis
  subshelf: profiles
  tags: series, csv
  added: "2026-11-16"
  featured: false
---

# Series gap list

List timestamps that a regular series is missing between the earliest and latest parsed values. Do not fill a gap and do not invent a close, a price, or a count for a missing slot. The grid rules are in [references/intervals.md](references/intervals.md).

## Steps

1. Confirm the file, the timestamp column, and the interval: `1d`, `1h`, or `1m`. If the interval is something else, say so and stop.
2. Run `python3 scripts/list_gaps.py` with `--column` and `--interval`. The sample is [assets/sample.csv](assets/sample.csv).
3. Report start, end, present, expected, missing, duplicates, and unparsed. List each `gap=` line the script printed.
4. If the script prints `refused=span-too-wide`, report that and do not guess the missing stamps.
5. Check that every reported gap falls strictly between start and end and is not a timestamp present in the file.

## Example

User: Which daily bars are missing in `assets/sample.csv`? Column `ts`, interval `1d`.

Agent: start 2026-11-10, end 2026-11-13, present 3, expected 4, missing 1. The only gap is 2026-11-12. No close is invented for that day. duplicates=0. unparsed=0.

## Boundaries

A gap list is not a market briefing and not a trade signal. Do not carry the previous close into the hole. A session note that uses quotes the user actually supplied belongs to market-data-briefing.
