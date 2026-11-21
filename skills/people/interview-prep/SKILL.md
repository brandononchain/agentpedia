---
name: interview-prep
description: >-
  Create structured interview plans with competency-based questions and
  scorecards. Trigger with "interview plan for", "interview questions for", "how
  should the user interview", "scorecard for", or when the user is preparing to
  interview candidates.
license: Apache-2.0
metadata:
  category: people
  subshelf: interviews
  tags: interview, prep, people
  added: "2026-11-21"
  featured: false
  source: import
  author: Anthropic
  authorUrl: "https://github.com/anthropics"
  authorKind: organization
  curator: Brandon
  upstream: anthropics/knowledge-work-plugins
  upstreamCommit: 0e0fcacddcc892eb92a1b7873ff9d68159c47571
  upstreamPath: human-resources/skills/interview-prep/SKILL.md
  upstreamLicense: Apache-2.0
  copyright: Copyright Anthropic
---

# Interview prep

Do this one job: an interview prep. Adapted from `anthropics/knowledge-work-plugins` at commit `0e0fcacddcc8` (Apache-2.0). Copyright Anthropic

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Structured: Same questions for all candidates in the role
3. Competency-based: Map questions to specific skills and behaviors
4. Evidence-based: Use behavioral and situational questions
5. Diverse panel: Multiple perspectives reduce bias
6. Scored: Use rubrics, not gut feelings
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Draft an interview prep from the notes in this message. Leave any figure I did not state as unknown.

Agent: A short interview prep that uses only those notes, names the gaps, and points at the check that would show it is done.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
