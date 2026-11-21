---
name: write-spec
description: >-
  Write a feature spec or PRD from a problem statement or feature idea. Use when
  turning a vague idea or user request into a structured document, scoping a
  feature with goals and non-goals, defining success metrics and acceptance
  criteria, or breaking a big ask into a phased spec
license: Apache-2.0
metadata:
  category: product
  subshelf: specs
  tags: write, spec, product
  added: "2026-11-21"
  featured: false
  source: import
  author: Anthropic
  authorUrl: "https://github.com/anthropics"
  authorKind: organization
  curator: Brandon
  upstream: anthropics/knowledge-work-plugins
  upstreamCommit: 0e0fcacddcc892eb92a1b7873ff9d68159c47571
  upstreamPath: product-management/skills/write-spec/SKILL.md
  upstreamLicense: Apache-2.0
  copyright: Copyright Anthropic
---

# Write spec

Do this one job: a write spec. Adapted from `anthropics/knowledge-work-plugins` at commit `0e0fcacddcc8` (Apache-2.0). Copyright Anthropic

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. A feature name ("SSO support")
3. A problem statement ("Enterprise customers keep asking for centralized auth")
4. A user request ("Users want to export their data as CSV")
5. A vague idea ("We should do something about onboarding drop-off")
6. User problem: What problem does this solve? Who experiences it?
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Draft a write spec from the notes in this message. Leave any figure I did not state as unknown.

Agent: A short write spec that uses only those notes, names the gaps, and points at the check that would show it is done.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
