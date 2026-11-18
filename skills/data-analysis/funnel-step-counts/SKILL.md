---
name: funnel-step-counts
description: >-
  Counts distinct actors at each step of an ordered funnel and the drop from the
  previous step. Use when the user asks how many people reached each stage in an
  event export.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/count_funnel.py. No network and no extra
  packages.
metadata:
  category: data-analysis
  subshelf: metrics
  tags: funnel, metrics
  added: "2026-11-16"
  featured: false
---

# Funnel step counts

Count how many distinct actors have each step the user named, and how many have that step plus every earlier step. The count is presence of labels, not the clock order of events. The rule is in [references/step-order.md](references/step-order.md).

## Steps

1. Confirm the file, the actor column, the step column, and the ordered step list. If any of those is missing, ask. Do not invent a step.
2. Run `python3 scripts/count_funnel.py` with `--actor`, `--step`, and `--steps`. The sample is [assets/sample.csv](assets/sample.csv).
3. Report `raw`, `ordered`, `drop_from_previous`, and `of_first` for each step, exactly as printed.
4. Report `unknown_labels` and `skipped_rows`. An actor who has a later label but not an earlier one stays in `raw` and stays out of `ordered`.
5. Check that each ordered count is less than or equal to that step's raw count, and that `of_first` uses the first step's ordered count as its denominator. Do not turn the fraction into a significance claim.

## Example

User: Count `assets/sample.csv`. Actor is `actor`, step is `step`, order is view, signup, paid.

Agent: view ordered 3 of 3. signup ordered 2 of 3, drop 1. paid raw 2, ordered 1 of 3, drop 1, because cara has `paid` and not `signup`. unknown_labels=0. skipped_rows=0.

## Boundaries

Do not drop an actor to make the last step match its raw count. Do not compute a p-value. A metric spec with no rows belongs to metric-definition. An experiment write-up belongs to experiment-log.
