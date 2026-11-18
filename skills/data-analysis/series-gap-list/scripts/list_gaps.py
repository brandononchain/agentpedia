#!/usr/bin/env python3
"""List missing timestamps on a regular grid. Does not fill or invent values."""

from __future__ import annotations

import argparse
import csv
import re
from datetime import datetime, timedelta
from pathlib import Path

DATE_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")
DATETIME_RE = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::(\d{2}))?Z?$"
)
MAX_SLOTS = 100_000
SHOW_GAPS = 40
INTERVALS = {"1d": timedelta(days=1), "1h": timedelta(hours=1), "1m": timedelta(minutes=1)}


def parse_stamp(raw: str) -> datetime | None:
    text = raw.strip()
    if DATE_RE.fullmatch(text):
        try:
            return datetime.strptime(text, "%Y-%m-%d")
        except ValueError:
            return None
    match = DATETIME_RE.fullmatch(text)
    if not match:
        return None
    seconds = match.group(6) or "00"
    try:
        return datetime.strptime(
            f"{match.group(1)}-{match.group(2)}-{match.group(3)} {match.group(4)}:{match.group(5)}:{seconds}",
            "%Y-%m-%d %H:%M:%S",
        )
    except ValueError:
        return None


def bucket(stamp: datetime, interval: str) -> datetime:
    if interval == "1d":
        return stamp.replace(hour=0, minute=0, second=0, microsecond=0)
    if interval == "1h":
        return stamp.replace(minute=0, second=0, microsecond=0)
    return stamp.replace(second=0, microsecond=0)


def format_bucket(stamp: datetime, interval: str) -> str:
    if interval == "1d":
        return stamp.strftime("%Y-%m-%d")
    if interval == "1h":
        return stamp.strftime("%Y-%m-%dT%H")
    return stamp.strftime("%Y-%m-%dT%H:%M")


def list_gaps(path: Path, column: str, interval: str) -> str:
    if interval not in INTERVALS:
        raise SystemExit("interval must be 1d, 1h, or 1m")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        if column not in fields:
            listed = ", ".join(fields) if fields else "(none)"
            raise SystemExit(f"column not found: {column}. columns: {listed}")
        rows = list(reader)

    seen: set[datetime] = set()
    duplicates = 0
    unparsed = 0
    date_only = 0
    for row in rows:
        raw = (row.get(column) or "").strip()
        if raw == "":
            unparsed += 1
            continue
        if interval != "1d" and DATE_RE.fullmatch(raw):
            date_only += 1
            unparsed += 1
            continue
        stamp = parse_stamp(raw)
        if stamp is None:
            unparsed += 1
            continue
        slot = bucket(stamp, interval)
        if slot in seen:
            duplicates += 1
            continue
        seen.add(slot)

    lines = [
        f"column={column}",
        f"interval={interval}",
        f"rows={len(rows)}",
        f"unparsed={unparsed}",
        f"date_only_rejected={date_only}",
        f"duplicates={duplicates}",
    ]
    if not seen:
        lines.append("present=0")
        lines.append("missing=0")
        lines.append("gaps_shown=0")
        return "\n".join(lines)

    start = min(seen)
    end = max(seen)
    step = INTERVALS[interval]
    expected_slots = int((end - start) / step) + 1
    lines.extend(
        [
            f"start={format_bucket(start, interval)}",
            f"end={format_bucket(end, interval)}",
            f"present={len(seen)}",
        ]
    )
    if expected_slots > MAX_SLOTS:
        lines.append(f"refused=span-too-wide expected={expected_slots}")
        return "\n".join(lines)

    missing: list[datetime] = []
    cursor = start
    while cursor <= end:
        if cursor not in seen:
            missing.append(cursor)
        cursor += step
    lines.append(f"expected={expected_slots}")
    lines.append(f"missing={len(missing)}")
    shown = missing[:SHOW_GAPS]
    lines.append(f"gaps_shown={len(shown)}")
    lines.append(f"gaps_omitted={len(missing) - len(shown)}")
    for slot in shown:
        lines.append(f"gap={format_bucket(slot, interval)}")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--column", required=True)
    parser.add_argument("--interval", required=True, choices=sorted(INTERVALS))
    args = parser.parse_args()
    if not args.csv_path.is_file():
        raise SystemExit(f"file not found: {args.csv_path}")
    print(list_gaps(args.csv_path, args.column, args.interval))


if __name__ == "__main__":
    main()
