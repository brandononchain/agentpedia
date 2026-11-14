---
name: subscription-renewal-watch
description: >-
  Projects the next date and an annualized amount for repeated charges in a
  CSV the user exported. Use when the user asks which subscriptions renew. A
  projected date is not a bill, and the skill does not contact a bank.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/renewal_watch.py. No network and no extra
  packages.
metadata:
  category: personal-life
  subshelf: renewals
  tags: subscriptions, renewals
  added: "2026-11-13"
  featured: false
---

# Subscription renewal watch

Group charges the user already exported and project a next date only when the gaps fit a cadence. The windows are in [references/cadence.md](references/cadence.md). Do not call a bank, and do not treat the projection as a bill.

## Steps

1. Confirm the CSV has `date`, `merchant`, and `amount`. If the export uses other headers, ask the user to rename them. Do not guess which column is the amount. The fixture is [assets/sample.csv](assets/sample.csv), and those merchant names are labels in the file.
2. Run `python3 scripts/renewal_watch.py` on that file.
3. Report `rows`, `charges`, `merchants`, `recurring`, `annualized_total`, and `annualized_skipped` as printed. For each merchant, report cadence, last amount, annualized amount, next date, and whether it was projected.
4. Check the report. Add every numeric annualized value and confirm it equals `annualized_total`. Confirm every merchant line is a merchant in the file. Say that a `projected=yes` date is the last charge plus the gap, not a bill the merchant sent.
5. If the user asks whether to cancel a charge, say the file does not say that. Do not move money.

## Example

User: Run the fixture `assets/sample.csv`. Do not contact a bank.

Agent: The script prints `rows=9`, `charges=9`, `merchants=4`, `recurring=3`, `annualized_total=402.00`, `annualized_skipped=1`. Design seat is monthly, gap 30, annualized 180.00, next 2026-11-14. Domain registrar is yearly, annualized 14.00, next 2027-11-03. News stand is weekly, annualized 208.00, next 2026-10-27. City transit is one charge, cadence unknown, annualized skipped. 180.00 + 14.00 + 208.00 = 402.00. The 2.75 transit row is not in that total. No merchant was added, and nothing was paid.

## Boundaries

Do not invent a price, a cadence, or a next date the script did not print. Do not call a charge fraud because the amount changed. This is a reading of one file, not tax advice and not a reason to cancel.
