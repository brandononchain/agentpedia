---
name: roadmap-update
description: >-
  Update, create, or reprioritize the user product roadmap. Use when adding a
  new initiative and deciding what moves to make room, shifting priorities after
  new information comes in, moving timelines due to a dependency slip, or
  building a Now/Next/Later view from scratch
license: Apache-2.0
metadata:
  category: product
  subshelf: roadmaps
  tags: roadmap, update, product
  added: "2026-11-21"
  featured: false
  source: import
  author: Anthropic
  authorUrl: "https://github.com/anthropics"
  authorKind: organization
  curator: Brandon
  upstream: anthropics/knowledge-work-plugins
  upstreamCommit: 0e0fcacddcc892eb92a1b7873ff9d68159c47571
  upstreamPath: product-management/skills/roadmap-update/SKILL.md
  upstreamLicense: Apache-2.0
  copyright: Copyright Anthropic
---

# Roadmap update

Do this one job: a roadmap update. Adapted from `anthropics/knowledge-work-plugins` at commit `0e0fcacddcc8` (Apache-2.0). Copyright Anthropic

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Pull current roadmap items with their statuses, assignees, and dates
3. Identify items that are overdue, at risk, or recently completed
4. Surface any items without clear owners or dates
5. Ask the user to describe their current roadmap or paste/upload it
6. Accept any format: list, table, spreadsheet, screenshot, or prose description
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Draft a roadmap update from the notes in this message. Leave any figure I did not state as unknown.

Agent: A short roadmap update that uses only those notes, names the gaps, and points at the check that would show it is done.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
