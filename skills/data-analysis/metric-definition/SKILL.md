---
name: metric-definition
description: >-
  Writes a metric spec with grain, formula, filters, and known caveats. Use when
  the user asks to define a KPI, a funnel step, or what a reported number means.
license: Apache-2.0
metadata:
  category: data-analysis
  tags: metrics, data
  added: "2026-11-06"
  featured: false
---

# Metric definition

Write a metric spec that two analysts would compute the same way. If a choice is not specified, mark it as an open question instead of picking a flattering definition.

## Steps

1. Name the metric and the decision it is meant to inform.
2. State the grain: one row per what, and the time window.
3. Write the formula in words and, when the user supplied fields, in those field names. List inclusions and exclusions.
4. Record caveats: late-arriving events, deleted rows, bots, internal traffic, and timezone.
5. Validate the spec by checking that the formula uses only fields the user named, or that missing fields are listed as open questions. Do not fill them in.

## Example

User: Define activation as a workspace that sends 10 invoices in its first 14 days. Exclude staff workspaces. Grain is one workspace.

Agent: Activation rate is activated workspaces divided by workspaces created in the cohort. A workspace is activated when it has 10 non-deleted invoices with `sent_at` inside 14 days of `workspace.created_at`, and `workspace.staff` is false. Timezone is not specified — open question. Staff exclusion uses the field the user named.

## Boundaries

Do not change the threshold to make a number look better. Do not present the spec as already approved.
