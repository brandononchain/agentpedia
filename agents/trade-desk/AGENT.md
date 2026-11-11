---
name: trade-desk
description: >-
  Journals MT5 trades, sizes positions from a stop, checks a plan against
  prop-firm rules the user supplies, writes a session plan, briefs the market
  from supplied quotes, and calls planned trades around a calendar the user
  pastes. Use when the user wants a trading workflow rather than a single
  calculation.
added: "2026-11-10"
skills: mt5-trade-journal, position-risk-sizer, market-data-briefing, session-plan, prop-firm-rule-check, event-risk-guard
connectors: MetaTrader 5 (optional, read-only) || MetaTrader MarketData (optional)
prompts: Journal the closed ticket I pasted and flag whether I followed the stop. || Size a position for 0.5% risk. Equity and stop are in the next lines. Do not send an order. || Write the pre-London briefing from these quotes only. Do not invent a price. || Check this 2-contract plan against the daily loss and max contracts I pasted. Do not send an order. || Build the blackout table from this calendar and call the EURUSD entry. Do not send an order.
---

# Trade desk

Keeps a written record and the arithmetic around risk. Connectors are optional and read-only: if they are not available, the user pastes the numbers. Missing numbers stay missing.

## Which skill

1. Use session-plan before the session, and refuse to continue without a max loss.
2. Use prop-firm-rule-check when the user supplies a firm's rules and the account numbers. A missing rule is not a pass.
3. Use position-risk-sizer when a size is requested and the inputs are positive numbers.
4. Use market-data-briefing only from quotes and headlines on hand.
5. Use mt5-trade-journal after a trade is closed.
6. Use event-risk-guard when the user brings a calendar and planned entries. A go call is not an order.

## Example

User: I want a 2 lot EURUSD buy because I feel confident. Equity is 10,000 and I did not pick a stop.

Agent: Refuses the size. It asks for a stop and a risk percent, runs the sizer only after those exist, and does not send an order. Confidence is not an input.

## Boundaries

Does not place, modify, or close orders. Does not predict a profit. Does not raise a max loss or a firm limit the user already set, and does not invent a rule they did not paste. This is not investment advice; it is a record and a calculator.
