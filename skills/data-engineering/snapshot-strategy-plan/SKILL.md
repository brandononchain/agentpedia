---
name: snapshot-strategy-plan
description: >-
  Plans a type-2 snapshot with a unique key, a timestamp or check strategy, and
  a hard-delete rule. Use when the user asks to keep history of a mutable table
  instead of overwriting the row.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/check_snapshot.py. No network and no extra
  packages.
metadata:
  category: data-engineering
  subshelf: schema
  tags: snapshots, scd
  added: "2026-11-17"
  featured: false
---

# Snapshot strategy plan

Plan one type-2 snapshot. Do not run it. A column add, rename, or drop stays with schema-expand-contract. This skill is the history of a row.

## Steps

1. Name the table and the unique key the user says identifies one entity. When the key is missing, ask. When they say the key is not unique, the plan cannot match rows.
2. Record the strategy they chose. `timestamp` needs an `updated_at` column they named. `check` needs the columns they named, or `all` when they said to compare every column. When they chose neither, leave the strategy unset. Do not pick one for them.
3. Record hard deletes only when they named `ignore`, `invalidate`, or `new_record`. Otherwise leave it unset. Do not fill the dbt default in as if they chose it.
4. Run `python3 scripts/check_snapshot.py` with those flags. Quote `status`, every `reason` line, and every `note` line. `full_refresh=ignored` means a full refresh will not rebuild this history.
5. Check the plan against the script. `status=ready` requires the strategy's fields and a key they said is unique. A missing field stays missing.

## Example

User: Snapshot `orders`. Unique key `id`, and it is unique. `updated_at` is reliable. When a source row is hard-deleted, keep a new row that says so. Do not run dbt.

Agent: Runs `python3 scripts/check_snapshot.py --unique-key id --key-unique yes --strategy timestamp --updated-at updated_at --hard-deletes new_record`. The script prints `status=ready`, `strategy=timestamp`, `hard_deletes=new_record`, `full_refresh=ignored`, and `note=new_record adds a row with dbt_is_deleted when a source row disappears`. dbt is not run.

## Boundaries

Do not invent `updated_at`. Do not drop the source table. Do not treat `hard_deletes=not-stated` as `ignore`. The note that names the default is a warning, not a choice.

## References

The field names and the full-refresh rule are summarized in [references/snapshot-config.md](references/snapshot-config.md) from dbt's snapshot docs. Quote the script for the ready check.
