---
name: spend-report
description: >-
  Totals a spend export by vendor and checks the grand total against the rows.
  Use when the user asks for a spend report, a bookkeeping summary, or where
  the money in a CSV went.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/sum_spend.py. No network and no extra
  packages.
metadata:
  category: finance-ops
  subshelf: spend
  tags: spend, bookkeeping
  added: "2026-11-10"
  featured: false
---

# Spend report

Add a spend file by vendor. Do not categorize a vendor into a budget the user did not define.

## Steps

1. Confirm the file has `vendor` and `amount`. Dates may be present and are not summed. The sample is [assets/sample.csv](assets/sample.csv).
2. Run `python3 scripts/sum_spend.py` on that file.
3. Report each vendor total and the grand total as printed. A blank vendor stays "(blank vendor)".
4. Check the report by adding the vendor lines and confirming they equal `total`. If they do not, show the script output and stop.
5. If the user also names a budget, say whether the grand total is under or over that number. Do not invent a budget.

## Example

User: Summarize `assets/sample.csv`.

Agent: Paper mill is 160.50. Ink shop is 15.25. The total is 175.75, and the two vendor lines add to that total. No budget was supplied, so none is mentioned.

## Boundaries

Do not move money, and do not call a vendor fraudulent because the amount is large.
