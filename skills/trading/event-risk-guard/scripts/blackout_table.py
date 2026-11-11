#!/usr/bin/env python3
"""Build blackout windows around calendar rows. Does not place a trade."""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

WATCHED_NAMES = ("cpi", "fomc", "nfp", "eia crude")


def parse_time(value: str) -> datetime:
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise SystemExit(f"not a timestamp: {value}") from exc
    if parsed.tzinfo is None:
        raise SystemExit(f"timestamp needs a timezone: {value}")
    return parsed.astimezone(timezone.utc)


def watched(name: str, impact: str) -> bool:
    lowered = name.strip().lower()
    if impact.strip().lower() == "high":
        return True
    return any(token in lowered for token in WATCHED_NAMES)


def main() -> int:
    parser = argparse.ArgumentParser(description="Print blackout windows for a calendar CSV.")
    parser.add_argument("csv_path")
    parser.add_argument("--before", type=int, required=True, help="Minutes before the release.")
    parser.add_argument("--after", type=int, required=True, help="Minutes after the release.")
    args = parser.parse_args()
    if args.before < 0 or args.after < 0:
        raise SystemExit("before and after must be zero or positive")

    path = Path(args.csv_path)
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or not {"name", "release_utc"} <= set(reader.fieldnames):
            raise SystemExit("csv needs name and release_utc columns")
        rows = list(reader)

    print("name\trelease_utc\tblackout_start\tblackout_end\timpact\tsymbols\twatched")
    counted = 0
    for row in rows:
        release = parse_time(row["release_utc"])
        start = release - timedelta(minutes=args.before)
        end = release + timedelta(minutes=args.after)
        impact = (row.get("impact") or "").strip() or "not stated"
        symbols = (row.get("symbols") or "").strip() or "not stated"
        flag = "yes" if watched(row["name"], impact if impact != "not stated" else "") else "no"
        print(
            "\t".join(
                [
                    row["name"].strip(),
                    release.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    end.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    impact,
                    symbols,
                    flag,
                ]
            )
        )
        counted += 1
    print(f"rows={counted}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
