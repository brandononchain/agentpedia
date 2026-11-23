---
name: case-brief
description: >-
  Brief a case in the user preferred format. In drill-me mode, makes the student
  state the holding first. Use when the user says "brief [case]", "what's the
  holding in", "case brief", or pastes a case
license: Apache-2.0
metadata:
  category: education
  subshelf: practice
  tags: case, brief, education
  added: "2026-11-23"
  featured: false
  source: import
  author: Anthropic
  authorUrl: "https://github.com/anthropics"
  authorKind: organization
  curator: Brandon
  upstream: anthropics/claude-for-legal
  upstreamCommit: 4a6c651889c97cc9140580363c73e0eb17379c2b
  upstreamPath: law-student/skills/case-brief/SKILL.md
  upstreamLicense: Apache-2.0
  copyright: Copyright Anthropic
---

# Case brief

Do this one job: a case brief. Adapted from `anthropics/claude-for-legal` at commit `4a6c651889c9` (Apache-2.0). Copyright Anthropic

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Apply the workflow below.
3. Brief in the student's format. If drill-me mode: ask the student to state the holding first.
4. If you paste the case text: I extract holding/rule/reasoning from what's in front of me. Confident.
5. If the case has famous-but-contested interpretations: I give the majority read and [VERIFY: check your casebook and professor's framing].
6. Ask the student what they already got from reading: the facts, the issue, the holding as they understand it.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Draft a case brief from the notes in this message. Leave any figure I did not state as unknown.

Agent: A short case brief that uses only those notes, names the gaps, and points at the check that would show it is done.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
