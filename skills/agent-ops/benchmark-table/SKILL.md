---
name: benchmark-table
description: >-
  Lays out benchmark numbers the user already measured, with the case count and
  the metric they named. Use when the user asks to compare agent runs and has
  the scores in hand.
license: Apache-2.0
metadata:
  category: agent-ops
  tags: benchmarks, evals
  added: "2026-11-10"
  featured: false
---

# Benchmark table

Put measured numbers in a table. Do not average runs they did not give you, and do not crown a winner from one case.

## Steps

1. Name the metric in their words (pass count, exact match, minutes). If two notes use different metrics, do not put them in one column.
2. One row per run they listed: the agent or the prompt name, the case count, the metric value, and the date if they gave one.
3. If they ask for a comparison, subtract only when both rows share a metric and a case count. Show the arithmetic.
4. Check the table so no cell contains a number that is not in their notes. A missing case count stays blank, and a blank cell is not treated as zero.
5. Say whether the table is enough to prefer one run. It is not, when the case count is missing or the runs used different cases.

## Example

User: Run A passed 8 of 10 cases. Run B passed 9 of 10 on the same cases yesterday.

Agent: Both rows are "passed of 10". The difference is 1 case. The table does not call B the better agent beyond that one metric on that set. No other metric is invented.

## Boundaries

Do not fabricate a score, a latency, or a cost. Do not declare a general winner.
