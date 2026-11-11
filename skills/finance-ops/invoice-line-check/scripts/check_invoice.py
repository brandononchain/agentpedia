#!/usr/bin/env python3
"""Sum invoice lines and compare them to a stated total."""

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
    if len(sys.argv) not in {2, 3}:
        print("usage: python3 scripts/check_invoice.py <csv> [expected_total]", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    total = Decimal("0")
    rows = 0
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not {"qty", "unit_price"} <= set(reader.fieldnames):
            raise SystemExit("csv needs qty and unit_price columns")
        for row in reader:
            rows += 1
            total += money(row["qty"]) * money(row["unit_price"])
    print(f"rows={rows}")
    print(f"total={total:.2f}")
    if len(sys.argv) == 3:
        expected = money(sys.argv[2])
        print("match" if total == expected else f"mismatch expected={expected:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
