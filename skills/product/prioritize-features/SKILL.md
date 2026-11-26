---
name: prioritize-features
description: >-
  Ranks a feature backlog by impact, effort, risk, and fit with the objective
  the user states. Use when the user asks which features to do next or for a
  top-five cut of a backlog.
license: MIT
metadata:
  category: product
  subshelf: discovery
  tags: prioritize, features, product
  added: "2026-11-26"
  featured: false
  source: import
  author: Pawel Huryn
  authorUrl: "https://github.com/phuryn"
  authorKind: person
  curator: Brandon
  upstream: phuryn/pm-skills
  upstreamCommit: 9af7bfd0bc47fdad43c2eaa7a43cd13918e7aaef
  upstreamPath: pm-product-discovery/skills/prioritize-features/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2026 Pawel Huryn
---

# Prioritize features

Do this one job: a ranked feature list. Adapted from `phuryn/pm-skills` at commit `9af7bfd0bc47` (MIT). Copyright (c) 2026 Pawel Huryn

## Steps

1. Confirm the product objective and the success metric the user stated. If either is missing, ask. Do not invent a metric.
2. List only the feature ideas the user supplied.
3. For each idea, note impact, effort, risk, and fit with that objective. Leave a cell blank when the user did not give the fact it needs.
4. Recommend at most five ideas, in order, with the trade-off that put each one above the rest. Name what was left off and why, using only those notes.
5. Validate that every score traces to a fact the user provided. Label the rest unknown.

## Example

User: Objective is to cut onboarding drop-off. Ideas are SSO, a CSV export, and a shorter signup form. Signup is the step where people leave. SSO is a large build. Export was requested twice.

Agent: The shorter signup form is first because the user tied drop-off to that step and did not call it a large build. SSO is last because the user called the build large and did not tie it to drop-off. Export stays in the middle. No idea is added.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
