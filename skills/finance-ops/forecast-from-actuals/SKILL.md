---
name: forecast-from-actuals
description: >-
  Projects a next period as the average of actuals the user supplies, and labels
  it as a projection. Use when the user asks for a forecast, a run-rate, or a
  simple forward view from past figures.
license: Apache-2.0
metadata:
  category: finance-ops
  tags: forecasting, bookkeeping
  added: "2026-11-10"
  featured: false
---

# Forecast from actuals

Average the periods the user typed. Call the result a projection. Do not dress it up as a prediction of profit.

## Steps

1. List the periods and amounts exactly as given. If a period is missing, leave it out and say which one was skipped. Do not fill it with zero unless the user said the value was zero.
2. The projection for the next period is the arithmetic mean of the amounts you kept. Show the sum and the count.
3. Label the result "projection from the listed actuals". Do not apply a growth rate they did not ask for.
4. If they ask for a range, also show the smallest and largest actual. Do not invent a confidence interval.
5. Check the mean by multiplying it by the count and comparing it to the sum, within one cent. If it does not match, recompute before you hand it back.

## Example

User: Actuals were 100, 130, and 160 for the last three months. What is next month if we assume the average?

Agent: Sum 390, count 3, projection 130.00 from those actuals. The smallest was 100 and the largest was 160. No growth rate is applied. 130 times 3 is 390, so the mean checks.

## Boundaries

This is not a financial forecast a lender should rely on, and it is not tax or investment advice. Do not add revenue the user hopes for.
