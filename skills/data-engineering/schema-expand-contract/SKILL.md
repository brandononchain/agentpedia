---
name: schema-expand-contract
description: >-
  Plans a schema migration as expand, migrate, then contract so old readers keep
  working. Use when the user asks to add, rename, or drop a warehouse column
  without taking the table down.
license: Apache-2.0
metadata:
  category: data-engineering
  tags: schema, migrations
  added: "2026-11-10"
  featured: false
---

# Schema expand and contract

Write the three phases for one column change. Do not run the migration. An application rollout checklist is a different skill; this one is the table.

## Steps

1. State the change in one line: add, rename, retype, or drop, and the column. A rename is a drop of the old name, so it needs all three phases.
2. Expand: the additive SQL the user would run, or "not stated" if they want you to draft it only after they confirm the type. Draft SQL only with types they gave.
3. Migrate: backfill, then writers, then readers, as three checks. A check is unmet until the user says it happened.
4. Contract: the drop, gated on the user confirming no remaining reader. If they want the drop in the same change as the add, say the plan is not safe to run as one step.
5. Check the plan so the drop never appears in the expand phase.

## Example

User: Rename `orders.total` to `orders.amount`. Both are integers. Old jobs still select `total`.

Agent: Expand adds `amount` and does not drop `total`. Migrate backfills `amount` from `total`, switches writers, then switches readers. Contract drops `total` only after those jobs stop selecting it. The rename is not one statement.

## Boundaries

Do not connect to a database, and do not schedule the drop.

## References

The phase split follows parallel change, credited in [references/parallel-change.md](references/parallel-change.md).
