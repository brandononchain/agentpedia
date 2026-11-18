#!/usr/bin/env python3
"""Check an incremental strategy against the dbt adapter table.

The table is the one dbt publishes for dbt v2 or the v1 Latest track:
https://docs.getdbt.com/docs/build/incremental-strategy
An older track can omit a strategy this script marks as listed.
"""

from __future__ import annotations

import argparse
import sys

# append, merge, delete+insert, insert_overwrite, microbatch
LISTED: dict[str, set[str]] = {
    "postgres": {"append", "merge", "delete+insert", "microbatch"},
    "redshift": {"append", "merge", "delete+insert", "microbatch"},
    "bigquery": {"merge", "insert_overwrite", "microbatch"},
    "spark": {"append", "merge", "insert_overwrite", "microbatch"},
    "databricks": {"append", "merge", "delete+insert", "insert_overwrite", "microbatch"},
    "snowflake": {"append", "merge", "delete+insert", "insert_overwrite", "microbatch"},
    "trino": {"append", "merge", "delete+insert", "microbatch"},
    "fabric": {"append", "merge", "delete+insert", "microbatch"},
    "athena": {"append", "merge", "insert_overwrite", "microbatch"},
    "teradata": {"append", "merge", "delete+insert", "microbatch"},
    "duckdb": {"append", "merge", "delete+insert", "microbatch"},
    "clickhouse": {"append", "delete+insert", "insert_overwrite"},
}

STRATEGIES = {"append", "merge", "delete+insert", "insert_overwrite", "microbatch"}
ALIASES = {
    "delete-insert": "delete+insert",
    "insert-overwrite": "insert_overwrite",
}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(2)


def normalize_adapter(value: str) -> str:
    name = value.strip().lower()
    if name.startswith("dbt-"):
        name = name[4:]
    return name


def normalize_strategy(value: str) -> str:
    name = value.strip().lower()
    return ALIASES.get(name, name)


def split_key(value: str) -> list[str]:
    if value.strip() == "":
        return []
    parts = [part.strip() for part in value.split(",")]
    if any(part == "" for part in parts):
        fail("unique key has an empty column")
    return parts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adapter", default="")
    parser.add_argument("--strategy", default="")
    parser.add_argument("--unique-key", default="")
    parser.add_argument("--key-nullable", choices=("yes", "no"), default="")
    parser.add_argument("--full-refresh", choices=("yes", "no"), default="")
    args = parser.parse_args()

    adapter = normalize_adapter(args.adapter)
    strategy = normalize_strategy(args.strategy)
    if strategy and strategy not in STRATEGIES:
        fail(
            "strategy must be append, merge, delete+insert, insert_overwrite, or microbatch"
        )
    key = split_key(args.unique_key)

    if not strategy:
        listed = "not-stated"
    elif not adapter:
        listed = "not-stated"
    elif adapter not in LISTED:
        listed = "unknown"
    elif strategy in LISTED[adapter]:
        listed = "yes"
    else:
        listed = "no"

    notes: list[str] = []
    if strategy and not adapter:
        notes.append("adapter was not named, so the support table was not applied")
    elif adapter and not strategy:
        notes.append("strategy was not chosen, so the support table was not applied")
    elif adapter and adapter not in LISTED:
        notes.append("this adapter is not in the published table")
    elif listed == "no":
        notes.append("this strategy is not in the published table for this adapter")

    if strategy == "append":
        notes.append("append inserts rows and does not use unique_key to skip duplicates")
    elif strategy == "merge" and not key:
        notes.append("merge without a unique_key behaves like append")
    elif strategy == "merge" and key:
        notes.append("merge updates a row with the same unique_key and inserts the rest")
    elif strategy == "delete+insert" and not key:
        notes.append("delete+insert needs a unique_key")
    elif strategy == "delete+insert" and key:
        notes.append("delete+insert replaces matching unique_key rows and does not keep history")
    elif strategy == "insert_overwrite":
        notes.append(
            "insert_overwrite replaces whole partitions and does not use unique_key"
        )
    elif strategy == "microbatch":
        notes.append("microbatch batches on an event_time column; this check does not judge that column")

    if args.key_nullable == "yes" and key:
        notes.append("a null in the unique key can fail to match and produce duplicate rows")
    elif args.key_nullable == "yes":
        notes.append("key_nullable was set but no unique key was named")
    if args.full_refresh == "yes":
        notes.append("full refresh drops the existing table and rebuilds it")

    print(f"adapter={adapter or 'not-stated'}")
    print(f"strategy={strategy or 'not-stated'}")
    print(f"strategy_listed={listed}")
    print(f"unique_key={','.join(key) if key else 'not-stated'}")
    print(f"key_nullable={args.key_nullable or 'not-stated'}")
    print(f"full_refresh={args.full_refresh or 'not-stated'}")
    for note in notes:
        print(f"note={note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
