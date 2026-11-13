#!/usr/bin/env python3
"""Build an SRT or WebVTT cue sheet from timed lines the user already wrote.

Does not transcribe audio. A character budget applies only when --max-chars is set.
WebVTT rules followed here are from the W3C WebVTT specification: the file
starts with WEBVTT, end time is after start time, cue starts are in
non-decreasing order, and cue text does not contain the arrow sequence.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ARROW = "-->"


def parse_time(value: str) -> int:
    text = value.strip()
    if "." in text:
        clock, frac = text.split(".", 1)
    elif "," in text:
        clock, frac = text.split(",", 1)
    else:
        raise SystemExit(f"timestamp needs milliseconds: {value}")
    if not frac.isdigit() or not 1 <= len(frac) <= 3:
        raise SystemExit(f"timestamp needs milliseconds: {value}")
    millis = int(frac.ljust(3, "0"))
    parts = clock.split(":")
    if len(parts) not in (2, 3):
        raise SystemExit(f"not a cue timestamp: {value}")
    try:
        numbers = [int(part) for part in parts]
    except ValueError as exc:
        raise SystemExit(f"not a cue timestamp: {value}") from exc
    if any(number < 0 for number in numbers):
        raise SystemExit(f"not a cue timestamp: {value}")
    if len(numbers) == 2:
        hours = 0
        minutes, seconds = numbers
    else:
        hours, minutes, seconds = numbers
    if minutes > 59 or seconds > 59:
        raise SystemExit(f"not a cue timestamp: {value}")
    return ((hours * 60 + minutes) * 60 + seconds) * 1000 + millis


def format_vtt(millis: int) -> str:
    hours, remainder = divmod(millis, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    seconds, fraction = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{fraction:03d}"


def format_srt(millis: int) -> str:
    return format_vtt(millis).replace(".", ",")


def load_cues(path: Path) -> list[tuple[int, int, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        if not {"start", "end", "text"} <= fields:
            raise SystemExit("csv needs start, end, and text columns")
        cues: list[tuple[int, int, str]] = []
        for index, row in enumerate(reader, start=2):
            start_raw = (row.get("start") or "").strip()
            end_raw = (row.get("end") or "").strip()
            text = row.get("text") or ""
            if start_raw == "" and end_raw == "" and text.strip() == "":
                continue
            if start_raw == "" or end_raw == "":
                raise SystemExit(f"row {index} is missing a timestamp")
            if text.strip() == "":
                raise SystemExit(f"row {index} is missing cue text")
            if "\n" in text or "\r" in text:
                raise SystemExit(f"row {index} text must be one line")
            cues.append((parse_time(start_raw), parse_time(end_raw), text.strip()))
    return cues


def render(cues: list[tuple[int, int, str]], fmt: str) -> str:
    blocks: list[str] = []
    if fmt == "vtt":
        blocks.append("WEBVTT\n")
    for index, (start, end, text) in enumerate(cues, start=1):
        if fmt == "srt":
            timing = f"{format_srt(start)} {ARROW} {format_srt(end)}"
            blocks.append(f"{index}\n{timing}\n{text}\n")
        else:
            timing = f"{format_vtt(start)} {ARROW} {format_vtt(end)}"
            blocks.append(f"{timing}\n{text}\n")
    return "\n".join(blocks).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Write an SRT or WebVTT cue sheet.")
    parser.add_argument("csv_path")
    parser.add_argument("--format", choices=("srt", "vtt"), required=True)
    parser.add_argument("--max-chars", type=int, help="Cue text budget. Omit to skip the check.")
    args = parser.parse_args()
    if args.max_chars is not None and args.max_chars < 1:
        raise SystemExit("max-chars must be a positive integer")
    cues = load_cues(Path(args.csv_path))

    end_after_start = all(end > start for start, end, _text in cues)
    ordered = all(
        cues[index][0] >= cues[index - 1][0] for index in range(1, len(cues))
    )
    overlap = any(
        cues[index][0] < cues[index - 1][1] for index in range(1, len(cues))
    )
    arrow_rows = [index for index, (_s, _e, text) in enumerate(cues, start=1) if ARROW in text]
    if args.max_chars is None:
        over_budget = 0
        budget = "not-set"
    else:
        over_budget = sum(1 for _s, _e, text in cues if len(text) > args.max_chars)
        budget = str(args.max_chars)
    longest = max((len(text) for _s, _e, text in cues), default=0)
    writable = end_after_start and ordered and not arrow_rows
    ready = writable and over_budget == 0 and len(cues) > 0

    report = [
        f"cues={len(cues)}",
        f"format={args.format}",
        f"end_after_start={'yes' if end_after_start else 'no'}",
        f"ordered={'yes' if ordered else 'no'}",
        f"overlap={'yes' if overlap else 'no'}",
        f"arrow_in_text={len(arrow_rows)}",
        f"over_budget={over_budget}",
        f"char_budget={budget}",
        f"longest_chars={longest}",
        f"ready={'yes' if ready else 'no'}",
    ]
    sys.stdout.write("\n".join(report) + "\n")
    if writable and cues:
        sys.stdout.write("cue_file:\n")
        sys.stdout.write(render(cues, args.format))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
