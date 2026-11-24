---
name: release-notes
description: >-
  Generate user-facing release notes from tickets, PRDs, or changelogs. Creates
  clear, engaging summaries organized by category (new features, improvements,
  fixes). Use when writing release notes, creating changelogs, announcing
  product updates, or summarizing what shipped
license: MIT
metadata:
  category: product
  subshelf: specs
  tags: release, notes, product
  added: "2026-11-24"
  featured: false
  source: import
  author: Pawel Huryn
  authorUrl: "https://github.com/phuryn"
  authorKind: person
  curator: Brandon
  upstream: phuryn/pm-skills
  upstreamCommit: 9af7bfd0bc47fdad43c2eaa7a43cd13918e7aaef
  upstreamPath: pm-execution/skills/release-notes/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2026 Pawel Huryn
---

# Release notes

Do this one job: a release notes. Adapted from `phuryn/pm-skills` at commit `9af7bfd0bc47` (MIT). Copyright (c) 2026 Pawel Huryn

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Read the tickets, changelog, or PRD the user supplied. Extract what changed, who it affects, and the user benefit.
3. Sort each item into new features, improvements, fixes, breaking changes, or deprecations.
4. Lead every line with the user benefit. Leave out class names and ticket ids a user of the product cannot act on.
5. Mark a breaking change only when the source says the user must migrate or change a call.
6. Do not announce work the source does not say shipped.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Draft a release notes from the notes in this message. Leave any figure I did not state as unknown.

Agent: A short release notes that uses only those notes, names the gaps, and points at the check that would show it is done.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
