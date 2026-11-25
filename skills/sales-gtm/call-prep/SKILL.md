---
name: call-prep
description: >-
  Prepares a pre-call brief from notes the user already has: attendees, the
  objective, prior context, and discovery questions. Use when the user asks
  to prep for a meeting or a sales call.
license: Apache-2.0
metadata:
  category: sales-gtm
  subshelf: discovery
  tags: call, prep, sales
  added: "2026-11-25"
  featured: false
  source: import
  author: Anthropic
  authorUrl: "https://github.com/anthropics"
  authorKind: organization
  curator: Brandon
  upstream: anthropics/knowledge-work-plugins
  upstreamCommit: 5e504ae11498f2b8daa30d86b7dab97b2ecd8092
  upstreamPath: sales/skills/call-prep/SKILL.md
  upstreamLicense: Apache-2.0
  copyright: Copyright Anthropic
---

# Call prep

Do this one job: a pre-call brief. Adapted from `anthropics/knowledge-work-plugins` at commit `5e504ae11498` (Apache-2.0). Copyright Anthropic

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. List attendees, account, and the open opportunity only when the notes name them. Use a dash when a field is absent. Do not invent a title, a stage, or a dollar amount.
3. State the objective as what should be true after the call that is not true before, in the user's words.
4. Draft three to five discovery questions that the notes do not already answer. Skip a question the last call already closed.
5. List objections and commitments only when a prior note states them. Do not add an objection from a guess about the company.
6. End with what to bring: a fact, a quote, or a file the user already named. Show the brief and wait.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Tomorrow with Northwind, attendees Ada (procurement) and Ben (security). Last call they asked for SOC2 and said budget is frozen until Q3. Objective is to learn who signs.

Agent: A brief that names Ada and Ben, the SOC2 ask, and the Q3 freeze, with questions only about who signs. No deal size, because the notes never stated one.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
