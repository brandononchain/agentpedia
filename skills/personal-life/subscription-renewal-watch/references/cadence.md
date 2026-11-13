# How a renewal is projected

The script reads only the CSV. It does not call a bank, a card network, or a subscription manager. Column names in a real export vary, so the file has to use `date`, `merchant`, and `amount` before the script runs. A date is `YYYY-MM-DD`. An amount is a plain decimal. A leading byte-order mark, which spreadsheet exports often add, is ignored.

Rows for one merchant on the same calendar day are one charge. The amounts on that day are added before any gap is measured. The merchant name is matched without regard to case. The spelling on the first row is the one printed.

A merchant with one charge has cadence `unknown`. A next date is not projected from a single charge.

When there are two or more charges, the gap is the lower median of the day counts between consecutive charges. An even count uses the lower of the two middle gaps, so the next date is a whole day.

The gap maps to a cadence only inside these windows:

- weekly: 6 to 8 days, annualized as the latest amount times 52
- monthly: 27 to 33 days, annualized as the latest amount times 12
- yearly: 360 to 370 days, annualized as the latest amount times 1

Any other gap is `irregular`. Irregular charges are not annualized and have no next date. The windows are this skill's rule, not a classification a bank published.

If the latest amount is zero or negative, annualized is `skipped` and nothing is projected, even when the gap fits a window. `amount_changed=yes` means the collapsed charges are not all the same amount. The annualized figure uses the latest amount only.

`projected=yes` means the next date is the last charge date plus the gap. That date is not a bill and not a price from the merchant. `annualized_total` adds only the annualized figures that are numbers.
