#!/usr/bin/env python3
"""Choose transcript spans that fit a runtime the user set.

Must-keep spans are never dropped. Optional spans fill leftover time in file
order. The script does not rewrite quote text and does not trim a media file.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


def parse_stamp(value: str) -> int:
    text = value.strip()
    parts = text.split(":")
    if len(parts) not in (2, 3):
        raise SystemExit(f"not a span timestamp: {value}")
    try:
        numbers = [int(part) for part in parts]
    except ValueError as exc:
        raise SystemExit(f"not a span timestamp: {value}") from exc
    if any(number < 0 for number in numbers):
        raise SystemExit(f"not a span timestamp: {value}")
    if len(numbers) == 2:
        hours = 0
        minutes, seconds = numbers
    else:
        hours, minutes, seconds = numbers
    if minutes > 59 or seconds > 59:
        raise SystemExit(f"not a span timestamp: {value}")
    return hours * 3600 + minutes * 60 + seconds


def format_stamp(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def load_spans(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        if not {"start", "end", "text", "must"} <= fields:
            raise SystemExit("csv needs start, end, text, and must columns")
        spans: list[dict] = []
        previous_end: int | None = None
        for index, row in enumerate(reader, start=2):
            start_raw = (row.get("start") or "").strip()
            end_raw = (row.get("end") or "").strip()
            text = (row.get("text") or "").strip()
            must_raw = (row.get("must") or "").strip().lower()
            if start_raw == "" and end_raw == "" and text == "" and must_raw == "":
                continue
            if start_raw == "" or end_raw == "":
                raise SystemExit(f"row {index} is missing a timestamp")
            if text == "":
                raise SystemExit(f"row {index} is missing text")
            if must_raw not in {"yes", "no"}:
                raise SystemExit(f"row {index} must be yes or no")
            start = parse_stamp(start_raw)
            end = parse_stamp(end_raw)
            if end <= start:
                raise SystemExit(f"row {index} ends before it starts")
            if previous_end is not None and start < previous_end:
                raise SystemExit(f"row {index} overlaps the previous span")
            previous_end = end
            spans.append(
                {
                    "start": start,
                    "end": end,
                    "text": text,
                    "must": must_raw == "yes",
                }
            )
    return spans


def line_for(span: dict) -> str:
    flag = "yes" if span["must"] else "no"
    start = format_stamp(span["start"])
    end = format_stamp(span["end"])
    return f"{start}-{end} must={flag} {span['text']}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Fit marked spans to a target runtime.")
    parser.add_argument("csv_path")
    parser.add_argument("--target-seconds", type=int, required=True)
    args = parser.parse_args()
    if args.target_seconds < 1:
        raise SystemExit("target-seconds must be a positive integer")
    spans = load_spans(Path(args.csv_path))
    must_seconds = sum(span["end"] - span["start"] for span in spans if span["must"])
    over = must_seconds > args.target_seconds
    # Optional spans share only the time left after every must-keep span.
    # A later required span is never squeezed out by an earlier optional one.
    optional_room = 0 if over else args.target_seconds - must_seconds
    used_optional = 0
    kept: list[dict] = []
    skipped: list[dict] = []
    for span in spans:
        if span["must"]:
            kept.append(span)
            continue
        if over:
            skipped.append(span)
            continue
        duration = span["end"] - span["start"]
        if used_optional + duration <= optional_room:
            kept.append(span)
            used_optional += duration
        else:
            skipped.append(span)
    kept_seconds = sum(span["end"] - span["start"] for span in kept)
    ready = not over and kept_seconds <= args.target_seconds and len(spans) > 0
    report = [
        f"spans={len(spans)}",
        f"target_seconds={args.target_seconds}",
        f"must_keep_seconds={must_seconds}",
        f"must_keep_over_target={'yes' if over else 'no'}",
        f"kept={len(kept)}",
        f"kept_seconds={kept_seconds}",
        f"remaining_seconds={args.target_seconds - kept_seconds}",
        f"ready={'yes' if ready else 'no'}",
        "kept_lines:",
        *[line_for(span) for span in kept],
        "skipped_lines:",
        *[line_for(span) for span in skipped],
    ]
    sys.stdout.write("\n".join(report) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
