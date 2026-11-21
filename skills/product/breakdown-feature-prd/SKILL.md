---
name: breakdown-feature-prd
description: >-
  Prompt for creating Product Requirements Documents (PRDs) for new features,
  based on an Epic. Use when the user asks for a breakdown feature prd.
license: MIT
metadata:
  category: product
  subshelf: specs
  tags: breakdown, feature, prd, product
  added: "2026-11-21"
  featured: false
  source: import
  author: "GitHub, Inc."
  authorUrl: "https://github.com/github"
  authorKind: organization
  curator: Brandon
  upstream: github/awesome-copilot
  upstreamCommit: f10fdb8b2660ce85c98f220b2f1ca24653768a5c
  upstreamPath: skills/breakdown-feature-prd/SKILL.md
  upstreamLicense: MIT
  copyright: "Copyright GitHub, Inc."
---

# Breakdown feature prd

Do this one job: a breakdown feature prd. Adapted from `github/awesome-copilot` at commit `f10fdb8b2660` (MIT). Copyright GitHub, Inc.

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. A clear, concise, and descriptive name for the feature.
3. Link to the parent Epic PRD and Architecture documents.
4. Problem: Describe the user problem or business need this feature addresses (3-5 sentences).
5. Solution: Explain how this feature solves the problem.
6. Impact: What are the expected outcomes or metrics to be improved (e.g., user engagement, conversion rate, etc.)?
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Draft a breakdown feature prd from the notes in this message. Leave any figure I did not state as unknown.

Agent: A short breakdown feature prd that uses only those notes, names the gaps, and points at the check that would show it is done.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
