---
name: mt5-trade-journal
description: >-
  Records an MT5 trade with the setup, the risk taken, the result, and whether
  the plan held. Use when the user asks to journal a trade, review a closed
  position, or write up an MT5 deal.
license: Apache-2.0
compatibility: >-
  Reads numbers the user pastes or a MetaTrader 5 connector the user has already
  authorized. Does not send orders.
metadata:
  category: trading
  tags: mt5, journal
  added: "2026-11-10"
  featured: true
---

# MT5 trade journal

Write one journal entry for one closed trade. Use the template in [references/entry-template.md](references/entry-template.md). Numbers come from the user or from a MetaTrader tool the user has connected. Never invent a fill, a price, or a profit.

## Steps

1. Collect symbol, direction, volume, entry, stop, exit, and timestamps. If a field is missing, leave it blank and say so. Do not estimate it.
2. Record the planned risk in account currency and whether the position size matched that plan. Use the position-risk-sizer skill if the user asks for the math and the inputs are present.
3. Record the result the terminal reported, including costs if the user supplied them.
4. Write two lines: what the setup was supposed to be, and whether the user followed it. If the user did not say, write "not stated."
5. Validate the entry against the template. Every number must trace to the user or the terminal output. Save or show the entry. Do not place, modify, or close an order.

## Example

User: Journal a closed buy of 0.10 EURUSD, entry 1.0850, stop 1.0825, exit 1.0880, from the ticket they pasted. They say they moved the stop wider than planned.

Agent: The entry records those four prices and 0.10 lots, marks the stop as wider than planned, and leaves costs blank because they were not supplied. No order is sent.

## Boundaries

This skill records history. It does not predict the next trade, and it does not talk to the broker except to read a deal the user already asked to journal.
