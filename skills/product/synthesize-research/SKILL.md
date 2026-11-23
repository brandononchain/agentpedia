---
name: synthesize-research
description: >-
  Synthesize user research from interviews, surveys, and feedback into
  structured insights. Use when the user have a pile of interview notes, survey
  responses, or support tickets to make sense of, need to extract themes and
  rank findings by frequency and impact, or want to turn raw feedback into
  roadmap recommendations
license: Apache-2.0
metadata:
  category: product
  subshelf: roadmaps
  tags: synthesize, research, product
  added: "2026-11-23"
  featured: false
  source: import
  author: Anthropic
  authorUrl: "https://github.com/anthropics"
  authorKind: organization
  curator: Brandon
  upstream: anthropics/knowledge-work-plugins
  upstreamCommit: 2baf6d1eded3cd7aeff0b5c5918601a5799189b4
  upstreamPath: product-management/skills/synthesize-research/SKILL.md
  upstreamLicense: Apache-2.0
  copyright: Copyright Anthropic
---

# Synthesize research

Do this one job: a synthesize research. Adapted from `anthropics/knowledge-work-plugins` at commit `2baf6d1eded3` (Apache-2.0). Copyright Anthropic

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Key observations: What did users say, do, or experience?
3. Quotes: Verbatim quotes that illustrate important points
4. Behaviors: What users actually did (vs what they said they do)
5. Pain points: Frustrations, workarounds, and unmet needs
6. Positive signals: What works well, moments of delight
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Draft a synthesize research from the notes in this message. Leave any figure I did not state as unknown.

Agent: A short synthesize research that uses only those notes, names the gaps, and points at the check that would show it is done.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
