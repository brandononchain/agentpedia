---
name: invoice-line-check
description: >-
  Sums invoice lines and says whether they match the total printed on the
  invoice. Use when the user asks to check an invoice, a bill, or a vendor
  statement against its lines.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/check_invoice.py. No network and no extra
  packages.
metadata:
  category: finance-ops
  subshelf: invoices
  tags: invoices, bookkeeping
  added: "2026-11-10"
  featured: false
---

# Invoice line check

Add the lines. Compare them to the stated total. Do not pay the invoice.

## Steps

1. Confirm the file has `qty` and `unit_price`. The sample is [assets/sample.csv](assets/sample.csv).
2. Run `python3 scripts/check_invoice.py` with the file and, when the invoice shows a total, that total as the second argument.
3. Report `rows`, `total`, and `match` or `mismatch` exactly as printed. Do not round to something else.
4. If the script rejects a cell, name the row and stop. Do not guess the number.
5. Check that the stated total you passed is the one printed on the invoice, not a number you would have liked it to be.

## Example

User: Check `assets/sample.csv` against a printed total of 550.00.

Agent: The script prints `rows=2`, `total=550.00`, and `match`. The desk line is 400 and the two chairs are 150. Nothing is marked paid.

## Boundaries

This is arithmetic, not tax advice and not an approval to pay. A match does not mean the price was fair.
