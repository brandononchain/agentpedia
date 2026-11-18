# Snapshot fields the plan may use

dbt snapshots implement a type-2 slowly changing dimension: the previous version of a row stays, and the new version is inserted. The source for that behavior, and for the field names below, is [Add snapshots to your DAG](https://docs.getdbt.com/docs/build/snapshots). This note is the checklist the script enforces. It is not a copy of that page.

For the YAML config dbt documents from v1.9 onward:

- `strategy` is `timestamp` or `check`.
- `unique_key` is required. dbt uses it to match rows, so a key that is not unique will not line up.
- `timestamp` reads one `updated_at` column. dbt recommends it when that column changes with the row, because a new or dropped source column does not force an edit to the snapshot config.
- `check` reads `check_cols`, a list or `all`. dbt recommends naming the columns. The script accepts `all` and adds a note.
- On a `check` snapshot, an optional `updated_at` is used for the validity timestamps when it is set. When it is null, dbt uses the snapshot's own timestamp.
- `hard_deletes` is `ignore` (the default: no action for a deleted source row), `invalidate` (set `dbt_valid_to` on that row), or `new_record` (add a row with `dbt_is_deleted`).
- Snapshots ignore the `full_refresh` config and the `--full-refresh` flag. That flag does not drop the snapshot table.

`scripts/check_snapshot.py` prints `status=ready` only when the chosen strategy has its required fields and the user said the key is unique. When hard deletes were not stated, the line stays `hard_deletes=not-stated`. The default is described in a note and is not written back as the choice.
