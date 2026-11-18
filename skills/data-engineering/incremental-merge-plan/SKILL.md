---
name: incremental-merge-plan
description: >-
  Writes an incremental load plan with the unique key, the strategy, and the
  filter that keeps a rerun from duplicating rows. Use when the user asks how a
  dbt model should increment or whether a reload will double-count.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/check_strategy.py. No network and no extra
  packages.
metadata:
  category: data-engineering
  subshelf: contracts
  tags: dbt, incremental
  added: "2026-11-17"
  featured: false
---

# Incremental merge plan

Write the reload rule for one incremental model. Do not run it, and do not pick a strategy the user did not name. Column types stay with etl-column-contract.

## Steps

1. Name the model and the grain (one row means what). If either is missing, ask. If they already stated a grain, keep it.
2. Record the unique-key columns they named, and whether a key column can be null. Leave the key unset when they named none.
3. Record the strategy they chose: `append`, `merge`, `delete+insert`, `insert_overwrite`, or `microbatch`. Record the adapter they named. Leave either unset when they did not say. Do not substitute a strategy.
4. Run `python3 scripts/check_strategy.py` with those flags. Quote `strategy_listed` and every `note` line. When the script says the strategy is not listed, keep their strategy and say the published table does not include that pair.
5. Record the incremental filter they gave, column and comparison. When the comparison is `>` on a timestamp, say rows equal to the stored maximum can be skipped on the next run. When they gave no filter, write "filter not stated".
6. Pass full refresh as they asked. A yes adds the script note that a full refresh drops the existing table. When they ask how a new column lands on rows already stored, say `on_schema_change` does not backfill those rows.
7. Check the plan against the script output. Every key column and the strategy must be ones they named. Drop the rest.

## Example

User: Model `fct_orders`, one row per `order_id`. `order_id` is not null. Adapter BigQuery. Strategy `insert_overwrite`. Filter is `order_date >=` the max `order_date` already stored. Do not full refresh. Do not run dbt.

Agent: Runs `python3 scripts/check_strategy.py --adapter bigquery --strategy insert_overwrite --unique-key order_id --key-nullable no --full-refresh no`. The script prints `strategy_listed=yes` and `note=insert_overwrite replaces whole partitions and does not use unique_key`. Grain stays one row per `order_id`. Filter is `order_date >=` the stored max. `full_refresh=no`. dbt is not run.

## Boundaries

Do not connect to a warehouse or estimate a cost. `strategy_listed=yes` means the pair is on the dbt v2 or v1 Latest matrix in [scripts/check_strategy.py](scripts/check_strategy.py). It is not a probe of an older adapter install.

## References

Unique-key nulls, the incremental filter, `--full-refresh`, and `on_schema_change` are summarized in [references/strategies.md](references/strategies.md) from dbt's incremental docs. Quote the script for the adapter matrix. Do not restate that matrix from memory.
