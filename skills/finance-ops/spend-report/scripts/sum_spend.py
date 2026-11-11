#!/usr/bin/env python3
"""Total a spend CSV by vendor."""

from __future__ import annotations

import csv
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path


def money(value: str) -> Decimal:
    try:
        return Decimal(value.strip())
    except InvalidOperation as exc:
        raise SystemExit(f"not a number: {value}") from exc


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python3 scripts/sum_spend.py <csv>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    totals: dict[str, Decimal] = {}
    rows = 0
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not {"vendor", "amount"} <= set(reader.fieldnames):
            raise SystemExit("csv needs vendor and amount columns")
        for row in reader:
            rows += 1
            vendor = row["vendor"].strip() or "(blank vendor)"
            totals[vendor] = totals.get(vendor, Decimal("0")) + money(row["amount"])
    grand = sum(totals.values(), Decimal("0"))
    print(f"rows={rows}")
    for vendor in sorted(totals):
        print(f"{vendor}\t{totals[vendor]:.2f}")
    print(f"total={grand:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
