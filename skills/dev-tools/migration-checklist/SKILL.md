---
name: migration-checklist
description: >-
  Plans an expand-and-contract migration for a schema, an API, or a config flag.
  Use when the user asks how to migrate without a big-bang cutover or wants a
  migration checklist.
license: Apache-2.0
metadata:
  category: dev-tools
  subshelf: migrations
  tags: migrations
  added: "2026-11-07"
  featured: false
---

# Migration checklist

Plan a migration that can ship in small steps and roll back. Prefer expand, then migrate, then contract. Do not recommend a single irreversible rewrite unless the user has already ruled out a phased path and accepts the downtime.

## Steps

1. Restate the current shape, the target shape, and who reads or writes the thing being migrated.
2. Write the expand step: add the new field, endpoint, or flag while the old path still works.
3. Write the migrate step: how existing data or clients move, how to detect stragglers, and how to stop if the error rate rises.
4. Write the contract step: when the old path may be removed, and what observation proves it is unused.
5. Validate the plan by checking that each step is deployable on its own and that the first step is reversible. List the rollback for expand and migrate.

## Example

User: We need to rename `invoice.total` to `invoice.amount_cents` without downtime.

Agent: Expand — add `amount_cents` and write both fields. Migrate — backfill old rows, compare the two values on read, and alert on mismatch. Contract — stop writing `total` only after a full week of zero mismatches, then drop the old column in a later migration. Rollback of expand is to ignore the new column. Rollback of the backfill is to keep reading `total`.

## Boundaries

Do not drop the old path in the same change that introduces the new one. Do not hand-wave the backfill as "a script."
