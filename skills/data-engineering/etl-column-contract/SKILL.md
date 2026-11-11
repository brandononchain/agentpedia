---
name: etl-column-contract
description: >-
  Writes a source-to-target column contract with types, nulls, and a grain.
  Use when the user asks for an ETL or dbt mapping before a model is built.
license: Apache-2.0
metadata:
  category: data-engineering
  tags: etl, dbt
  added: "2026-11-10"
  featured: false
---

# ETL column contract

Write the contract for one target table from columns the user lists. Do not create the table.

## Steps

1. Name the source, the target, and the grain (one row means what). If the grain is missing, ask before mapping columns.
2. For each target column, record the source column, the type the user stated, whether nulls are allowed, and the rule when the source is null. If they did not state a type, write "type not stated".
3. Mark columns that are keys. A key with allowed nulls is a conflict; say so.
4. Check that every target column traces to a source column they named, or is labeled "derived" with the expression they gave. Drop invented columns.
5. If they mention a dbt test, record the test name they used (not null, unique, accepted values). Do not claim the test passed.

## Example

User: One row per order_id. Source orders.order_id is a string key, not null. orders.total_cents is an integer and may be null. Target column amount is total_cents divided by 100.

Agent: Grain is one row per order_id. order_id comes from orders.order_id, string, not null, key. amount is derived, total_cents / 100, and is null when total_cents is null. No test result is claimed. The table is not created.

## Boundaries

Do not run a warehouse query, and do not invent a column that would make the model look finished.

## References

Recording a not-null or unique check next to a column follows the idea of a data test in [dbt](https://docs.getdbt.com/docs/build/data-tests). This skill only writes the contract. It does not run dbt.
