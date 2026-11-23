---
name: onboarding
description: >-
  Generate an onboarding checklist and first-week plan for a new hire. Use when
  someone has a start date coming up, building the pre-start task list
  (accounts, equipment, buddy), scheduling Day 1 and Week 1, or setting
  30/60/90-day goals for a new team member
license: Apache-2.0
metadata:
  category: people
  subshelf: roles
  tags: onboarding, people
  added: "2026-11-23"
  featured: false
  source: import
  author: Anthropic
  authorUrl: "https://github.com/anthropics"
  authorKind: organization
  curator: Brandon
  upstream: anthropics/knowledge-work-plugins
  upstreamCommit: 2baf6d1eded3cd7aeff0b5c5918601a5799189b4
  upstreamPath: human-resources/skills/onboarding/SKILL.md
  upstreamLicense: Apache-2.0
  copyright: Copyright Anthropic
---

# Onboarding

Do this one job: an onboarding. Adapted from `anthropics/knowledge-work-plugins` at commit `2baf6d1eded3` (Apache-2.0). Copyright Anthropic

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. New hire name: Who's starting?
3. Team: Which team are they joining?
4. Start date: When do they start?
5. Manager: Who's their manager?
6. Customize for the role — An engineer's onboarding looks different from a designer's.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Draft an onboarding from the notes in this message. Leave any figure I did not state as unknown.

Agent: A short onboarding that uses only those notes, names the gaps, and points at the check that would show it is done.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
