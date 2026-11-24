---
name: socratic-drill
description: >-
  Socratic drilling — it asks, the user answer, it pushes back. Does NOT give
  the user the answer until the user earned it. Use when the user says "drill me
  on", "quiz me", "socratic", "test me on [subject]", or wants to study actively
license: Apache-2.0
metadata:
  category: education
  subshelf: assessment
  tags: socratic, drill, education
  added: "2026-11-23"
  featured: false
  source: import
  author: Anthropic
  authorUrl: "https://github.com/anthropics"
  authorKind: organization
  curator: Brandon
  upstream: anthropics/claude-for-legal
  upstreamCommit: 4a6c651889c97cc9140580363c73e0eb17379c2b
  upstreamPath: law-student/skills/socratic-drill/SKILL.md
  upstreamLicense: Apache-2.0
  copyright: Copyright Anthropic
---

# Socratic drill

Do this one job: a socratic drill. Adapted from `anthropics/claude-for-legal` at commit `4a6c651889c9` (Apache-2.0). Copyright Anthropic

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Apply the workflow below.
3. Ask a question on the topic. Wait for answer.
4. Push back. Ask follow-ups. Don't give the answer.
5. Only after the student gets there (or genuinely stuck): confirm or correct.
6. The stated rule and the uploaded rule disagree on a specific point — not a phrasing difference, not a level-of-detail difference, but a substantive contradiction.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Draft a socratic drill from the notes in this message. Leave any figure I did not state as unknown.

Agent: A short socratic drill that uses only those notes, names the gaps, and points at the check that would show it is done.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
