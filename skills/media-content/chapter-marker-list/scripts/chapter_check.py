#!/usr/bin/env python3
"""Check a user-timed chapter list against YouTube's published chapter rules.

Does not upload a video and does not invent a timestamp or a title.
The rules are the three requirements on YouTube's video-chapters help page:
the first timestamp is zero, there are at least three timestamps in ascending
order, and each chapter is at least 10 seconds.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

MIN_CHAPTERS = 3
MIN_LENGTH = 10


def parse_stamp(value: str) -> int:
    text = value.strip()
    parts = text.split(":")
    if len(parts) not in (2, 3):
        raise SystemExit(f"not a chapter timestamp: {value}")
    try:
        numbers = [int(part) for part in parts]
    except ValueError as exc:
        raise SystemExit(f"not a chapter timestamp: {value}") from exc
    if any(number < 0 for number in numbers):
        raise SystemExit(f"not a chapter timestamp: {value}")
    if len(numbers) == 2:
        hours = 0
        minutes, seconds = numbers
    else:
        hours, minutes, seconds = numbers
    if minutes > 59 or seconds > 59:
        raise SystemExit(f"not a chapter timestamp: {value}")
    return hours * 3600 + minutes * 60 + seconds


def parse_runtime(value: str) -> int:
    text = value.strip()
    if ":" in text:
        return parse_stamp(text)
    if text.isdigit():
        return int(text)
    raise SystemExit(f"not a runtime: {value}")


def format_stamp(seconds: int, with_hours: bool) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if with_hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def load_rows(path: Path) -> list[tuple[int, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        if "start" not in fields or "title" not in fields:
            raise SystemExit("csv needs start and title columns")
        rows: list[tuple[int, str]] = []
        for index, row in enumerate(reader, start=2):
            start_raw = (row.get("start") or "").strip()
            title = (row.get("title") or "").strip()
            if start_raw == "" and title == "":
                continue
            if start_raw == "":
                raise SystemExit(f"row {index} is missing a start")
            if title == "":
                raise SystemExit(f"row {index} is missing a title")
            if any(mark in title for mark in ("\n", "\r")):
                raise SystemExit(f"row {index} title must be one line")
            rows.append((parse_stamp(start_raw), title))
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Check YouTube chapter lines.")
    parser.add_argument("csv_path")
    parser.add_argument(
        "--runtime",
        help="Video length as seconds or a timestamp. Required to check the last chapter.",
    )
    args = parser.parse_args()
    rows = load_rows(Path(args.csv_path))
    runtime = parse_runtime(args.runtime) if args.runtime else None
    with_hours = any(start >= 3600 for start, _title in rows) or (
        runtime is not None and runtime >= 3600
    )

    lines: list[str] = []
    short = 0
    ascending = True
    previous: int | None = None
    for start, title in rows:
        if previous is not None:
            if start <= previous:
                ascending = False
            if start - previous < MIN_LENGTH:
                short += 1
        previous = start
        lines.append(f"{format_stamp(start, with_hours)} {title}")

    first_is_zero = bool(rows) and rows[0][0] == 0
    if runtime is None:
        last_length = "not-checked"
        last_ok = False
    elif not rows or runtime < rows[-1][0]:
        last_length = "before-last-start" if rows else "not-checked"
        last_ok = False
    else:
        gap = runtime - rows[-1][0]
        last_length = str(gap)
        last_ok = gap >= MIN_LENGTH
        if not last_ok:
            short += 1

    ready = (
        len(rows) >= MIN_CHAPTERS
        and first_is_zero
        and ascending
        and last_ok
        and short == 0
    )
    report = [
        f"chapters={len(rows)}",
        f"first_is_zero={'yes' if first_is_zero else 'no'}",
        f"ascending={'yes' if ascending else 'no'}",
        f"min_length_seconds={MIN_LENGTH}",
        f"short_chapters={short}",
        f"last_length={last_length}",
        f"runtime={'not-supplied' if runtime is None else runtime}",
        f"stamp_form={'hms' if with_hours else 'ms'}",
        f"ready={'yes' if ready else 'no'}",
        "description_lines:",
        *lines,
    ]
    sys.stdout.write("\n".join(report) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
