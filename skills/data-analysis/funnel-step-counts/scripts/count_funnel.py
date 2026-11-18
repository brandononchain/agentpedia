#!/usr/bin/env python3
"""Count distinct actors at each named funnel step. Presence only, not time order."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def count_funnel(path: Path, actor_column: str, step_column: str, steps: list[str]) -> str:
    if len(steps) != len(set(steps)):
        raise SystemExit("steps must be unique")
    if not steps:
        raise SystemExit("pass at least one step")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        missing = [name for name in (actor_column, step_column) if name not in fields]
        if missing:
            listed = ", ".join(fields) if fields else "(none)"
            raise SystemExit(f"column not found: {', '.join(missing)}. columns: {listed}")
        rows = list(reader)

    by_actor: dict[str, set[str]] = {}
    skipped = 0
    unknown: list[str] = []
    unknown_seen: set[str] = set()
    known = set(steps)
    for row in rows:
        actor = (row.get(actor_column) or "").strip()
        step = (row.get(step_column) or "").strip()
        if actor == "" or step == "":
            skipped += 1
            continue
        if step not in known:
            if step not in unknown_seen:
                unknown.append(step)
                unknown_seen.add(step)
            continue
        by_actor.setdefault(actor, set()).add(step)

    lines = [
        f"steps={','.join(steps)}",
        f"rows={len(rows)}",
        f"skipped_rows={skipped}",
        f"actors={len(by_actor)}",
        f"unknown_labels={len(unknown)}",
        f"unknown_label_sample={' | '.join(unknown[:5]) if unknown else '(none)'}",
    ]
    previous = None
    first_ordered = None
    for step in steps:
        raw = sum(1 for present in by_actor.values() if step in present)
        required = set(steps[: steps.index(step) + 1])
        ordered = sum(1 for present in by_actor.values() if required <= present)
        if first_ordered is None:
            first_ordered = ordered
        drop = 0 if previous is None else previous - ordered
        previous = ordered
        lines.append(
            f"step={step} raw={raw} ordered={ordered} drop_from_previous={drop} of_first={ordered}/{first_ordered}"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--actor", required=True)
    parser.add_argument("--step", required=True)
    parser.add_argument("--steps", required=True, help="Comma-separated step labels, in funnel order")
    args = parser.parse_args()
    if not args.csv_path.is_file():
        raise SystemExit(f"file not found: {args.csv_path}")
    steps = [part.strip() for part in args.steps.split(",") if part.strip()]
    print(count_funnel(args.csv_path, args.actor, args.step, steps))


if __name__ == "__main__":
    main()
