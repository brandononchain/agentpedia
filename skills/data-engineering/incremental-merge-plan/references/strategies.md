# How to read the strategy check

`scripts/check_strategy.py` encodes the adapter matrix on [About incremental strategy](https://docs.getdbt.com/docs/build/incremental-strategy). dbt says that matrix is for dbt v2 or the v1 Latest track, and that a strategy can be missing on an older track. `strategy_listed=yes` means the matrix includes the pair. It is not a probe of an adapter installed on a machine.

That page is also the source for what each built-in strategy does:

- `append` inserts the selected rows and does not look for a row that is already there.
- `merge` updates a row whose unique key is already in the table and inserts the rest. With no unique key, dbt says merge behaves like append.
- `delete+insert` deletes target rows for that unique key, then inserts. It does not keep the previous version of the row. dbt points at snapshots, not this strategy, for type-2 history.
- `insert_overwrite` replaces whole partitions. dbt says it does not use `unique_key`.
- `microbatch` splits a large time series into batches on an `event_time` column. The checker does not judge that column.

[Incremental models](https://docs.getdbt.com/docs/build/incremental-models) is the source for the rest of the plan. A unique key should not contain nulls, or matching can fail and duplicate rows. `--full-refresh` drops the existing table and rebuilds it. None of the `on_schema_change` settings backfill a new column onto rows already stored. The documented incremental examples filter with `>=` so a row that shares the latest timestamp is not skipped.

Quote the script. Do not invent a strategy, and do not mark an adapter as listed because it is a common warehouse.
