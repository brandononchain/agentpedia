#!/usr/bin/env python3
"""Check that a type-2 snapshot plan has the fields the chosen strategy needs.

Field names follow dbt snapshot config for v1.9 and later:
https://docs.getdbt.com/docs/build/snapshots
The script does not run dbt.
"""

from __future__ import annotations

import argparse
import sys

STRATEGIES = {"timestamp", "check"}
HARD_DELETES = {"ignore", "invalidate", "new_record"}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(2)


def columns(value: str) -> list[str]:
    if value.strip() == "":
        return []
    parts = [part.strip() for part in value.split(",")]
    if any(part == "" for part in parts):
        fail("check cols has an empty column")
    if "all" in parts and parts != ["all"]:
        fail("check cols all cannot be combined with column names")
    return parts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--unique-key", default="")
    parser.add_argument("--key-unique", choices=("yes", "no"), default="")
    parser.add_argument("--strategy", default="")
    parser.add_argument("--updated-at", default="")
    parser.add_argument("--check-cols", default="")
    parser.add_argument("--hard-deletes", default="")
    args = parser.parse_args()

    strategy = args.strategy.strip().lower()
    if strategy and strategy not in STRATEGIES:
        fail("strategy must be timestamp or check")
    hard = args.hard_deletes.strip().lower()
    if hard and hard not in HARD_DELETES:
        fail("hard deletes must be ignore, invalidate, or new_record")
    key = [part.strip() for part in args.unique_key.split(",") if args.unique_key.strip()]
    if args.unique_key.strip() and any(part.strip() == "" for part in args.unique_key.split(",")):
        fail("unique key has an empty column")
    checked = columns(args.check_cols)
    updated = args.updated_at.strip()

    reasons: list[str] = []
    notes: list[str] = []
    if not key:
        reasons.append("unique-key-missing")
    if args.key_unique == "":
        reasons.append("uniqueness-not-stated")
    elif args.key_unique == "no":
        reasons.append("unique-key-not-unique")
    if not strategy:
        reasons.append("strategy-not-chosen")
    elif strategy == "timestamp":
        if not updated:
            reasons.append("timestamp-needs-updated-at")
        if checked:
            reasons.append("timestamp-does-not-use-check-cols")
    elif strategy == "check":
        if not checked:
            reasons.append("check-needs-columns")
        if checked == ["all"]:
            notes.append("dbt recommends naming check columns instead of all")
        if updated:
            notes.append("updated_at on a check snapshot is used for validity timestamps when it is set")

    if hard == "new_record":
        notes.append("new_record adds a row with dbt_is_deleted when a source row disappears")
    elif hard == "invalidate":
        notes.append("invalidate closes the current row by setting dbt_valid_to")
    elif hard == "ignore":
        notes.append("ignore leaves a deleted source row in the snapshot history")
    else:
        notes.append("hard deletes were not stated; the dbt default is ignore")

    status = "ready" if not reasons else "incomplete"
    print(f"status={status}")
    print(f"unique_key={','.join(key) if key else 'not-stated'}")
    print(f"key_unique={args.key_unique or 'not-stated'}")
    print(f"strategy={strategy or 'not-stated'}")
    print(f"updated_at={updated or 'not-stated'}")
    print(f"check_cols={','.join(checked) if checked else 'not-stated'}")
    print(f"hard_deletes={hard or 'not-stated'}")
    print("full_refresh=ignored")
    for reason in reasons:
        print(f"reason={reason}")
    for note in notes:
        print(f"note={note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
