#!/usr/bin/env python3
"""Check a coverage list against away dates. Does not store a code."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from datetime import datetime
from pathlib import Path

SECRETISH_RE = re.compile(
    r"(?i)\b(?:password|passcode|passphrase|pin|wifi password|alarm code|door code|gate code)\b"
    r".{0,24}\d{4,}"
)


def fail(message: str) -> None:
    raise SystemExit(message)


def parse_date(value: str, label: str):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        fail(f"{label} must be YYYY-MM-DD")


def one_line(value: str, row_number: int, label: str) -> str:
    if "\t" in value or "\n" in value or "\r" in value:
        fail(f"row {row_number} {label} must be one line")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Check a house-coverage list.")
    parser.add_argument("csv_path")
    parser.add_argument("--away-start", required=True)
    parser.add_argument("--away-end", required=True)
    args = parser.parse_args()
    away_start = parse_date(args.away_start, "away-start")
    away_end = parse_date(args.away_end, "away-end")
    if away_start > away_end:
        fail("away-start is after away-end")

    path = Path(args.csv_path)
    rows = []
    seen: set[str] = set()
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        needed = {"item", "owner", "window_start", "window_end", "instruction"}
        if not needed <= fields:
            fail("csv needs item, owner, window_start, window_end, and instruction columns")
        for index, row in enumerate(reader, start=2):
            item = one_line((row.get("item") or "").strip(), index, "item")
            owner = one_line((row.get("owner") or "").strip(), index, "owner")
            start_raw = (row.get("window_start") or "").strip()
            end_raw = (row.get("window_end") or "").strip()
            instruction = one_line((row.get("instruction") or "").strip(), index, "instruction")
            if item == "" and owner == "" and start_raw == "" and end_raw == "" and instruction == "":
                continue
            flags: list[str] = []
            window = "bad-date"
            if item == "" or owner == "" or instruction == "" or start_raw == "" or end_raw == "":
                flags.append("incomplete")
            else:
                try:
                    start = datetime.strptime(start_raw, "%Y-%m-%d").date()
                    end = datetime.strptime(end_raw, "%Y-%m-%d").date()
                except ValueError:
                    flags.append("incomplete")
                else:
                    window = f"{start.isoformat()}..{end.isoformat()}"
                    if start > end or start < away_start or end > away_end:
                        flags.append("outside")
            key = item.casefold()
            if key and key in seen:
                flags.append("duplicate")
            if key:
                seen.add(key)
            if SECRETISH_RE.search(item) or SECRETISH_RE.search(instruction):
                flags.append("secretish")
            rows.append((item, owner, window, instruction, flags or ["ok"]))

    def count(flag: str) -> int:
        return sum(1 for _item, _owner, _window, _instruction, flags in rows if flag in flags)

    ready = bool(rows) and all(flags == ["ok"] for *_rest, flags in rows)
    lines = [
        f"away={away_start.isoformat()}..{away_end.isoformat()}",
        f"items={len(rows)}",
        f"incomplete={count('incomplete')}",
        f"outside={count('outside')}",
        f"duplicate={count('duplicate')}",
        f"secretish={count('secretish')}",
        f"ready={'yes' if ready else 'no'}",
        "item\towner\twindow\tinstruction\tflags",
    ]
    for item, owner, window, instruction, flags in rows:
        lines.append("\t".join([item, owner, window, instruction, ",".join(flags)]))
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
