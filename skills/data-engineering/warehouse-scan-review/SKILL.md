---
name: warehouse-scan-review
description: >-
  Reads a warehouse query for partition filters, unbounded joins, and select-star
  scans. Use when the user asks why a BigQuery, Snowflake, Redshift, or dbt
  query might read more data than they expect.
license: Apache-2.0
metadata:
  category: data-engineering
  subshelf: warehouses
  tags: sql, warehouse
  added: "2026-11-10"
  featured: false
---

# Warehouse scan review

Say what the query text forces the warehouse to consider. Do not invent bytes scanned. A plain explanation of what the query returns belongs to sql-explain-plain. This skill is about scan cost.

## Steps

1. Name the engine only if the user named it. Otherwise say the engine is unspecified.
2. List each base table and whether the query filters that table on a column the user has called a partition, cluster, or sort key. If they did not name such a column, write "partition filter not shown".
3. Flag a join with no predicate, a `select *` on a table they described as wide, and a filter wrapped in a function if they said that function blocks pruning.
4. If they pasted a bytes-scanned figure from the engine, quote it. If they did not, label every risk "visible in the SQL, not measured".
5. Check that every table you named is in the query. Remove the rest.

## Example

User: This is BigQuery. `events` is partitioned on `event_date`. Query: `select * from events e join users u on true where e.event_date >= '2026-11-01'`.

Agent: Engine is BigQuery. `events` has a filter on the partition column. `users` has no filter. The join predicate is `true`, so the join is unbounded. `select *` is on `events`. Risks are visible in the SQL and not measured, because no bytes figure was pasted.

## Boundaries

Do not rewrite the query unless asked. Do not claim a slot, a warehouse credit, or a dollar cost you did not calculate from numbers the user gave.
