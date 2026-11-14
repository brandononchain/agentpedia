---
name: event-risk-guard
description: >-
  Builds a blackout window around high-impact releases the user supplies (CPI,
  FOMC, NFP, EIA crude inventories) and gives a go, reduce, or stand-aside call
  for each planned trade. Use when the user asks whether a trade sits on an
  economic release. Advisory only. It does not place trades.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/blackout_table.py. No network and no extra
  packages.
metadata:
  category: trading
  subshelf: risk
  tags: calendar, risk
  added: "2026-11-11"
  featured: false
---

# Event risk guard

Turn a calendar the user already has into a blackout table, then call each planned trade. This is advisory. It does not place, modify, or close a trade, and it is not investment advice.

## Steps

1. Take the calendar from the user. Required columns are `name` and `release_utc`. `impact` and `symbols` may be blank. If the minutes before and after the release are missing, ask. Do not invent a window or a release time.
2. Run `python3 scripts/blackout_table.py` on that file with `--before` and `--after`. The fixture is [assets/sample.csv](assets/sample.csv), and it is not a live calendar.
3. Treat a row as high-impact when the script prints `watched=yes`. That flag is on for CPI, FOMC, NFP, and EIA crude inventories, and for any row the user marked `high`. A `watched=no` row stays in the table and does not drive a call.
4. For each planned trade, compare the entry time with the watched blackouts whose `symbols` include that trade. `USD` covers pairs and dollar products the user said are dollar trades. `crude` covers the oil symbols they named. If `symbols` is `not stated`, do not guess the market.
5. Call the trade. Stand-aside when the entry time is inside a matching watched blackout, or when the symbols were not stated. Reduce when the entry is outside every matching blackout but the user did not name a stop. Go only when the entry is outside every matching blackout and a stop is named. Check the call against the printed start and end. Do not send an order.

## Example

User: Use `assets/sample.csv` with 15 minutes before and 15 after. Planned trade: buy EURUSD at 2026-11-13T13:20:00Z with a stop. Do not send an order.

Agent: The script prints `rows=5`. CPI is watched, blackout 2026-11-13T13:15:00Z to 2026-11-13T13:45:00Z, symbols USD. The EURUSD entry sits inside that window. Call: stand-aside. Consumer confidence is `watched=no` and does not change the call. No order is sent.

## Boundaries

Do not fetch a calendar, invent a release, or widen a window the user set. Do not turn a go call into an order. A go call is not a forecast.

## References

News blackouts are the same idea as the news line on prop-firm-rule-check: a time the user already decided not to trade. This skill builds the window table. It does not look up a firm's current rule.
