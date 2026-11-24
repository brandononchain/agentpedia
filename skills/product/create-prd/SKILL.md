---
name: create-prd
description: >-
  Create a lean, decision-ready Product Requirements Document with an 8-section
  template: summary, contacts, background, objective, market segments, value
  propositions (6-part JTBD template), solution, and release. Lean by default
  (about one to two pages), with a fuller spec on request. Use when writing a
  PRD.
license: MIT
metadata:
  category: product
  subshelf: specs
  tags: create, prd, product
  added: "2026-11-24"
  featured: false
  source: import
  author: Pawel Huryn
  authorUrl: "https://github.com/phuryn"
  authorKind: person
  curator: Brandon
  upstream: phuryn/pm-skills
  upstreamCommit: 9af7bfd0bc47fdad43c2eaa7a43cd13918e7aaef
  upstreamPath: pm-execution/skills/create-prd/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2026 Pawel Huryn
---

# Create prd

Do this one job: a create prd. Adapted from `phuryn/pm-skills` at commit `9af7bfd0bc47` (MIT). Copyright (c) 2026 Pawel Huryn

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Write a lean document, about one to two pages, with eight sections: summary, contacts, background, objective, market segments, value propositions, solution, and release.
3. Always include market segments and a six-part value proposition: who, why, what before, how, what after, and alternatives.
4. Keep a thin section to a line or two. Omit contacts when the user did not name any. Do not pad a section or write TBD.
5. Put unknown facts in assumptions and open questions. Do not state them as fact.
6. Name the smallest first version that would test the objective. Leave the success measure blank when the user did not supply one.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Draft a create prd from the notes in this message. Leave any figure I did not state as unknown.

Agent: A short create prd that uses only those notes, names the gaps, and points at the check that would show it is done.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
