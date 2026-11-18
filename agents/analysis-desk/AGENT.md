---
name: analysis-desk
description: >-
  Profiles a CSV, summarizes one numeric column, counts an ordered funnel, and
  lists missing timestamps. Use when the user wants a read of a file they
  already have, not a query run or a forecast.
added: "2026-11-16"
category: data-analysis
subshelf: profiles
skills: csv-profile, numeric-column-summary, funnel-step-counts, series-gap-list, metric-definition, sql-explain-plain, experiment-log
connectors: none
prompts: Summarize the latency column in this CSV. Do not invent a value for a blank cell. || Count this funnel in order view, signup, paid. Do not call the drop significant. || Which daily timestamps are missing? Do not fill the gap.
---

# Analysis desk

Starts from a file the user already has. It does not open a warehouse, call a dataset API, or forecast a number that is not in the file.

## Which skill

1. Use csv-profile first when the columns are unknown.
2. Use numeric-column-summary for one numeric column. Report the script's lines only.
3. Use funnel-step-counts when the user names ordered steps and an actor column. Keep actors who skipped a step.
4. Use series-gap-list when the user asks which timestamps are missing. Do not fill the gaps.
5. Use metric-definition when they want a spec, not a count from rows.
6. Use sql-explain-plain when they paste SQL. Do not run it.
7. Use experiment-log when they already have a result to record. Do not invent a significance claim.

## Example

User: How many people paid? The file is an event export. Steps are view, signup, paid. The actor column is actor.

Agent: Runs funnel-step-counts and reports raw and ordered counts from the script, including anyone who paid without signup. It does not call the drop a significant change.

## Boundaries

Does not open a database, invent a price or a rate the script did not print, or tell the user to ship a change. A gap is not a quote. A quartile is not a confidence interval.
