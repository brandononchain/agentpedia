#!/usr/bin/env python3
"""Size a position from equity, risk percent, and stop distance."""

from __future__ import annotations

import argparse


def size(equity: float, risk_pct: float, stop: float, value_per_unit: float) -> tuple[float, float]:
    if min(equity, risk_pct, stop, value_per_unit) <= 0:
        raise SystemExit("equity, risk percent, stop, and value per unit must be positive")
    risk_cash = equity * (risk_pct / 100.0)
    units = risk_cash / (stop * value_per_unit)
    return risk_cash, units


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--equity", type=float, required=True)
    parser.add_argument("--risk-pct", type=float, required=True)
    parser.add_argument("--stop", type=float, required=True, help="Stop distance in price units")
    parser.add_argument(
        "--value-per-unit",
        type=float,
        required=True,
        help="Account currency gained or lost when price moves 1.0 per unit",
    )
    args = parser.parse_args()
    risk_cash, units = size(args.equity, args.risk_pct, args.stop, args.value_per_unit)
    print(f"risk_cash={risk_cash:.2f}")
    print(f"units={units:.4f}")


if __name__ == "__main__":
    main()
