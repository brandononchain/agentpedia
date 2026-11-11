# Expand, then contract

A schema change that has to stay up while old and new readers both run can be split the way Martin Fowler describes parallel change: add the new shape, move readers and writers over, then remove the old shape. See [Parallel change](https://martinfowler.com/bliki/ParallelChange.html).

This shelf uses three phases and does not copy that article.

1. Expand. Add the new column or table. Old readers ignore it. Do not drop the old column in this phase.
2. Migrate. Backfill from the old column, then switch writers, then switch readers. Each of those is a separate step the user has to confirm.
3. Contract. Drop the old column only after the user says no reader still selects it.

Skipping from expand to drop is the failure this skill is meant to catch.
