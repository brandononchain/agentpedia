#!/usr/bin/env python3
"""Compare the newest timestamp in a CSV to warn and error ages.

Ages use the same periods as a dbt freshness config: minute, hour, or day.
https://docs.getdbt.com/reference/resource-configs/freshness
The script reads a file. It does not query a warehouse.
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

PERIOD_SECONDS = {"minute": 60, "hour": 3600, "day": 86400}
PERIOD_SUFFIX = {"minute": "m", "hour": "h", "day": "d"}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(2)


def parse_time(value: str, label: str) -> datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    if len(text) == 10 and text[4] == "-" and text[7] == "-":
        try:
            parsed = datetime.strptime(text, "%Y-%m-%d")
        except ValueError:
            fail(f"{label} is not a timestamp")
        return parsed.replace(tzinfo=timezone.utc)
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        fail(f"{label} is not a timestamp")
    if parsed.tzinfo is None:
        fail(f"{label} needs a timezone offset or Z")
    return parsed.astimezone(timezone.utc)


def threshold(count: int | None, period: str | None, flag: str) -> int | None:
    if count is None and not period:
        return None
    if count is None or not period:
        fail(f"{flag} needs both a count and a period")
    if count < 1:
        fail(f"{flag} count must be a positive integer")
    if period not in PERIOD_SECONDS:
        fail(f"{flag} period must be minute, hour, or day")
    return count * PERIOD_SECONDS[period]


def show_threshold(count: int | None, period: str | None) -> str:
    if count is None or not period:
        return "not-set"
    return f"{count}{PERIOD_SUFFIX[period]}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--column", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--warn-count", type=int)
    parser.add_argument("--warn-period")
    parser.add_argument("--error-count", type=int)
    parser.add_argument("--error-period")
    args = parser.parse_args()

    warn = threshold(args.warn_count, args.warn_period, "warn")
    error = threshold(args.error_count, args.error_period, "error")
    if warn is None and error is None:
        fail("set a warn threshold or an error threshold")
    as_of = parse_time(args.as_of, "as-of")
    if not args.csv_path.is_file():
        fail(f"file not found: {args.csv_path}")

    stamps: list[datetime] = []
    blank = 0
    rows = 0
    with args.csv_path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        if args.column not in fields:
            fail(f"csv needs a {args.column} column")
        for index, row in enumerate(reader, start=2):
            rows += 1
            raw = (row.get(args.column) or "").strip()
            if raw == "":
                blank += 1
                continue
            stamps.append(parse_time(raw, f"row {index} {args.column}"))

    newest = max(stamps) if stamps else None
    print(f"rows={rows}")
    print(f"nonempty={len(stamps)}")
    print(f"blank={blank}")
    print(f"max_loaded_at={newest.strftime('%Y-%m-%dT%H:%M:%SZ') if newest else 'none'}")
    print(f"as_of={as_of.strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print(f"warn_after={show_threshold(args.warn_count, args.warn_period)}")
    print(f"error_after={show_threshold(args.error_count, args.error_period)}")
    if newest is None:
        print("age_seconds=")
        print("status=error")
        print("reason=no-timestamp")
        return 0

    age = int((as_of - newest).total_seconds())
    print(f"age_seconds={age}")
    if error is not None and warn is not None and error <= warn:
        print("note=error threshold is not longer than the warn threshold")
    if age < 0:
        print("note=newest timestamp is after as-of")
    if error is not None and age > error:
        print("status=error")
    elif warn is not None and age > warn:
        print("status=warn")
    else:
        print("status=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
