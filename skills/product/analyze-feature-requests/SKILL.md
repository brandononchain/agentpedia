---
name: analyze-feature-requests
description: >-
  Groups feature requests the user supplied into themes and ranks the top
  three by impact, effort, risk, and fit with a goal the user stated. Use
  when the user asks to triage a backlog or prioritize customer requests.
license: MIT
metadata:
  category: product
  subshelf: discovery
  tags: analyze, feature, requests, product
  added: "2026-11-25"
  featured: false
  source: import
  author: Pawel Huryn
  authorUrl: "https://github.com/phuryn"
  authorKind: person
  curator: Brandon
  upstream: phuryn/pm-skills
  upstreamCommit: 9af7bfd0bc47fdad43c2eaa7a43cd13918e7aaef
  upstreamPath: pm-product-discovery/skills/analyze-feature-requests/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2026 Pawel Huryn
---

# Analyze feature requests

Do this one job: a priority of requests the user already has. Adapted from `phuryn/pm-skills` at commit `9af7bfd0bc47` (MIT). Copyright (c) 2026 Pawel Huryn

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Restate the product goal in the user's words. If no goal was stated, ask for one before ranking.
3. Group the requests into themes. Name a theme only when at least two requests share a problem. Keep a one-off request in its own row.
4. For each theme, say how it lines up with the stated goal. Use "unknown" when the user did not say who is affected or what it costs.
5. Pick at most three themes. Rank them only on impact, effort, risk, and goal fit that the user supplied. Leave a factor blank rather than scoring it.
6. For each pick, give the rationale in the customer's problem, not a solution they did not ask for, and name one alternative that is smaller.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Goal is to cut time-to-first-dashboard. Requests: CSV export (4 accounts), SSO (1 account), "the dashboard is slow" (11 accounts), and a dark mode (2 accounts). No effort estimates.

Agent: One theme, slow dashboard, ranked first on the stated goal and the count of 11. Effort stays unknown. CSV export and dark mode stay unranked. SSO stays a one-off.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
