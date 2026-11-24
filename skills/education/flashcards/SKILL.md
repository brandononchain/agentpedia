---
name: flashcards
description: >-
  Generate or drill flashcards for black-letter memorization — Leitner-style
  buckets, per-subject markdown storage, drill mode with self-assessment. Use
  when the user says "drill flashcards", "make flashcards from", "quiz me on
  cards", or wants to memorize rules
license: Apache-2.0
metadata:
  category: education
  subshelf: assessment
  tags: flashcards, education
  added: "2026-11-23"
  featured: false
  source: import
  author: Anthropic
  authorUrl: "https://github.com/anthropics"
  authorKind: organization
  curator: Brandon
  upstream: anthropics/claude-for-legal
  upstreamCommit: 4a6c651889c97cc9140580363c73e0eb17379c2b
  upstreamPath: law-student/skills/flashcards/SKILL.md
  upstreamLicense: Apache-2.0
  copyright: Copyright Anthropic
---

# Flashcards

Do this one job: a flashcards. Adapted from `anthropics/claude-for-legal` at commit `4a6c651889c9` (Apache-2.0). Copyright Anthropic

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Apply the framework below.
3. --drill (default): prioritize due cards + new; show Q, wait for answer, show A, take self-assessment, update buckets + next review.
4. --review: browse deck by bucket.
5. --stats: progress snapshot; flag stuck cards for verbal drill.
6. --session <n: focused N-card session, prioritized by prior misses + due cards; appends results to study-plan.yaml → session_history.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Draft a flashcards from the notes in this message. Leave any figure I did not state as unknown.

Agent: A short flashcards that uses only those notes, names the gaps, and points at the check that would show it is done.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
