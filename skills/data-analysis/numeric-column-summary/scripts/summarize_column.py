#!/usr/bin/env python3
"""Summarize one numeric CSV column. Prints only values computed from the file."""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal, InvalidOperation
from math import gcd
from pathlib import Path


def format_number(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def format_mean(total: Decimal, count: int) -> str:
    """Exact sum divided by the numeric count, as an integer or a reduced fraction."""
    sign, digits, exponent = total.as_tuple()
    numerator = int("".join(str(digit) for digit in digits) or "0")
    if sign:
        numerator = -numerator
    if exponent >= 0:
        numerator *= 10 ** exponent
        denominator = count
    else:
        denominator = count * (10 ** (-exponent))
    divisor = gcd(numerator, denominator)
    numerator //= divisor
    denominator //= divisor
    if denominator == 1:
        return str(numerator)
    return f"{numerator}/{denominator}"


def nearest_rank(sorted_values: list[Decimal], percent: int) -> Decimal:
    count = len(sorted_values)
    rank = (percent * count + 99) // 100
    rank = min(max(rank, 1), count)
    return sorted_values[rank - 1]


def parse_number(raw: str) -> Decimal | None:
    text = raw.strip()
    if text == "":
        return None
    try:
        value = Decimal(text)
    except InvalidOperation:
        return None
    if not value.is_finite():
        return None
    return value


def summarize(path: Path, column: str) -> str:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        if column not in fields:
            listed = ", ".join(fields) if fields else "(none)"
            raise SystemExit(f"column not found: {column}. columns: {listed}")
        rows = list(reader)

    numeric: list[Decimal] = []
    blank = 0
    non_numeric_cells = 0
    non_numeric_sample: list[str] = []
    for row in rows:
        raw = row.get(column) or ""
        if raw.strip() == "":
            blank += 1
            continue
        value = parse_number(raw)
        if value is None:
            non_numeric_cells += 1
            text = raw.strip()
            if text not in non_numeric_sample and len(non_numeric_sample) < 5:
                non_numeric_sample.append(text)
            continue
        numeric.append(value)

    sample = " | ".join(non_numeric_sample) if non_numeric_sample else "(none)"
    lines = [
        f"column={column}",
        f"rows={len(rows)}",
        f"numeric={len(numeric)}",
        f"blank={blank}",
        f"non_numeric={non_numeric_cells}",
        f"non_numeric_sample={sample}",
    ]
    if not numeric:
        lines.append("percentiles=not-computed")
        return "\n".join(lines)

    ordered = sorted(numeric)
    total = sum(ordered, Decimal("0"))
    lines.extend(
        [
            f"min={format_number(ordered[0])}",
            f"p25={format_number(nearest_rank(ordered, 25))}",
            f"median={format_number(nearest_rank(ordered, 50))}",
            f"p75={format_number(nearest_rank(ordered, 75))}",
            f"max={format_number(ordered[-1])}",
            f"sum={format_number(total)}",
            f"mean={format_mean(total, len(ordered))}",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--column", required=True)
    args = parser.parse_args()
    if not args.csv_path.is_file():
        raise SystemExit(f"file not found: {args.csv_path}")
    print(summarize(args.csv_path, args.column))


if __name__ == "__main__":
    main()
