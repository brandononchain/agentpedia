#!/usr/bin/env python3
"""Profile a CSV: rows, columns, empty cells, distinct counts, and samples."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def profile(path: Path, sample_size: int = 5) -> str:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    lines = [f"rows={len(rows)}", f"columns={len(fields)}"]
    if not fields:
        lines.append("no header row")
        return "\n".join(lines)
    for field in fields:
        values = [(row.get(field) or "") for row in rows]
        empty = sum(1 for value in values if value.strip() == "")
        distinct = len({value for value in values if value.strip() != ""})
        samples: list[str] = []
        for value in values:
            text = value.strip()
            if text and text not in samples:
                samples.append(text)
            if len(samples) >= sample_size:
                break
        shown = " | ".join(samples) if samples else "(none)"
        lines.append(
            f"{field}: empty={empty} distinct={distinct} sample={shown}"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    args = parser.parse_args()
    if not args.csv_path.is_file():
        raise SystemExit(f"file not found: {args.csv_path}")
    print(profile(args.csv_path))


if __name__ == "__main__":
    main()
