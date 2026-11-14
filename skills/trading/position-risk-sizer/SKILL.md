---
name: position-risk-sizer
description: >-
  Computes position size from account equity, a risk percent, and stop distance.
  Use when the user asks how large a position should be or for a lot or unit
  size from a fixed risk.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/size_position.py. No broker connection and no
  network.
metadata:
  category: trading
  subshelf: risk
  tags: risk, sizing
  added: "2026-11-10"
  featured: true
---

# Position risk sizer

Size a position so a stop-out loses a stated fraction of equity. Use [scripts/size_position.py](scripts/size_position.py). This is arithmetic, not a recommendation to take the trade.

## Steps

1. Collect equity, risk percent, stop distance in price units, and cash value of a 1.0 price move per unit (or per lot). If any input is missing or not positive, stop and ask. Do not assume a lot size.
2. Run `python3 scripts/size_position.py` with those flags. Risk cash is equity times risk percent. Units are risk cash divided by stop distance times value per unit.
3. Show the inputs, the risk cash, and the unit size. Round the way the user asks; otherwise keep four decimal places for units and two for cash.
4. State the assumption in one line: the stop is the exit, and costs are not included unless the user added them to the stop distance.
5. Validate by recomputing risk cash independently and checking that units times stop times value per unit equals that risk cash, within rounding. Do not place an order.

## Example

User: Equity 10,000, risk 0.5 percent, stop 25 pips, and each pip per lot is worth 1.

Agent: Runs the script with `--equity 10000 --risk-pct 0.5 --stop 25 --value-per-unit 1`. Reports risk cash 50.00 and size 2.0000 units. Assumption: costs are not in the stop. No order is placed.

## Boundaries

Do not raise the size to hit a profit target. Do not size a trade with no stop. Do not claim the stop will be filled at that price.
