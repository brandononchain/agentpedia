---
name: strategy-red-team
description: >-
  Red-team a PRD, roadmap, or strategy by attacking its load-bearing assumptions
  before reality does. Steelmans then attacks each claim, ranks failure modes by
  impact times likelihood times cheapness to test, and returns the cheapest
  test and kill criteria for each. Use when stress-testing a plan,
  pressure-testing a strategy, or preparing a document for review.
license: MIT
metadata:
  category: product
  subshelf: roadmaps
  tags: strategy, red, team, product
  added: "2026-11-24"
  featured: false
  source: import
  author: Pawel Huryn
  authorUrl: "https://github.com/phuryn"
  authorKind: person
  curator: Brandon
  upstream: phuryn/pm-skills
  upstreamCommit: 9af7bfd0bc47fdad43c2eaa7a43cd13918e7aaef
  upstreamPath: pm-execution/skills/strategy-red-team/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2026 Pawel Huryn
---

# Strategy red team

Do this one job: a strategy red team. Adapted from `phuryn/pm-skills` at commit `9af7bfd0bc47` (MIT). Copyright (c) 2026 Pawel Huryn

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Steelman, then attack. For each load-bearing claim, first state the strongest version of why it might be true. Then attack that — not a strawman. An attack on a weak version of the claim is worthless.
3. Write each failure mode as "Fails if ___." Be concrete and falsifiable. "Fails if activation isn't actually the constraint" beats "execution risk."
4. Rank by (impact if wrong) × (likelihood wrong) × (cheapness to test). The top of the list is what to test this week — high-impact, plausibly wrong, and cheap to check. Surface that ranking; don't bury the lede.
5. For each kill-assumption that survives, state the fail condition, the evidence to collect, the kill criterion, and the cheapest test.
6. Say which claims already hold. Do not manufacture a weakness the plan does not have.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Draft a strategy red team from the notes in this message. Leave any figure I did not state as unknown.

Agent: A short strategy red team that uses only those notes, names the gaps, and points at the check that would show it is done.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
