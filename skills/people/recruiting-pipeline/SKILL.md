---
name: recruiting-pipeline
description: >-
  Track and manage recruiting pipeline stages. Trigger with "recruiting update",
  "candidate pipeline", "how many candidates", "hiring status", or when the user
  discusses sourcing, screening, interviewing, or extending offers.
license: Apache-2.0
metadata:
  category: people
  subshelf: interviews
  tags: recruiting, pipeline, people
  added: "2026-11-23"
  featured: false
  source: import
  author: Anthropic
  authorUrl: "https://github.com/anthropics"
  authorKind: organization
  curator: Brandon
  upstream: anthropics/knowledge-work-plugins
  upstreamCommit: 2baf6d1eded3cd7aeff0b5c5918601a5799189b4
  upstreamPath: human-resources/skills/recruiting-pipeline/SKILL.md
  upstreamLicense: Apache-2.0
  copyright: Copyright Anthropic
---

# Recruiting pipeline

Do this one job: a recruiting pipeline. Adapted from `anthropics/knowledge-work-plugins` at commit `2baf6d1eded3` (Apache-2.0). Copyright Anthropic

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Pipeline velocity: Days per stage
3. Conversion rates: Stage-to-stage drop-off
4. Source effectiveness: Which channels produce hires
5. Offer acceptance rate: Offers extended vs. accepted
6. Time to fill: Days from req open to offer accepted
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Draft a recruiting pipeline from the notes in this message. Leave any figure I did not state as unknown.

Agent: A short recruiting pipeline that uses only those notes, names the gaps, and points at the check that would show it is done.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
