---
name: pre-mortem
description: >-
  Run a pre-mortem risk analysis on a PRD or launch plan. Categorizes risks as
  Tigers (real problems), Paper Tigers (overblown concerns), and Elephants
  (unspoken worries), then classifies as launch-blocking, fast-follow, or track.
  Use when preparing for launch, stress-testing a product plan, or identifying
  what could go wrong.
license: MIT
metadata:
  category: product
  subshelf: specs
  tags: pre, mortem, product
  added: "2026-11-24"
  featured: false
  source: import
  author: Pawel Huryn
  authorUrl: "https://github.com/phuryn"
  authorKind: person
  curator: Brandon
  upstream: phuryn/pm-skills
  upstreamCommit: 9af7bfd0bc47fdad43c2eaa7a43cd13918e7aaef
  upstreamPath: pm-execution/skills/pre-mortem/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2026 Pawel Huryn
---

# Pre mortem

Do this one job: a pre mortem. Adapted from `phuryn/pm-skills` at commit `9af7bfd0bc47` (MIT). Copyright (c) 2026 Pawel Huryn

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Imagine the launch 14 days out, then imagine it failed. List what went wrong using only the plan the user supplied.
3. Sort each risk into a Tiger (real and evidenced), a Paper Tiger (overblown), or an Elephant (unspoken and untested).
4. Mark each Tiger as launch-blocking, fast-follow, or track.
5. For every launch-blocking Tiger, name a mitigation and the decision still missing. Leave the owner blank when the user did not name one.
6. Do not invent revenue, adoption, or a reputation hit the plan did not state.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Draft a pre mortem from the notes in this message. Leave any figure I did not state as unknown.

Agent: A short pre mortem that uses only those notes, names the gaps, and points at the check that would show it is done.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
