---
name: user-stories
description: >-
  Writes user stories with a card, a conversation, and acceptance criteria from
  a feature the user describes. Use when the user asks for user stories,
  backlog items, or acceptance criteria for one feature.
license: MIT
metadata:
  category: product
  subshelf: specs
  tags: user, stories, product
  added: "2026-11-26"
  featured: false
  source: import
  author: Pawel Huryn
  authorUrl: "https://github.com/phuryn"
  authorKind: person
  curator: Brandon
  upstream: phuryn/pm-skills
  upstreamCommit: 9af7bfd0bc47fdad43c2eaa7a43cd13918e7aaef
  upstreamPath: pm-execution/skills/user-stories/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2026 Pawel Huryn
---

# User stories

Do this one job: user stories for one feature. Adapted from `phuryn/pm-skills` at commit `9af7bfd0bc47` (MIT). Copyright (c) 2026 Pawel Huryn

## Steps

1. Confirm the feature and the user role. If either is missing, ask. Do not invent a role or a second feature.
2. Write each story as a card (a title and one line), a short conversation of the intent, and acceptance criteria a tester could check.
3. Keep each story independent, small enough for one sprint, and tied to a benefit the user named.
4. If the user did not give a design link, write "design not supplied". Do not invent a URL.
5. Validate that every criterion traces to the feature description. Label anything else unknown.

## Example

User: Shoppers want a recently viewed row on the product page. Hide it on the first page of a session. Do not include the product they are on.

Agent: One story whose card is "Recently viewed". The conversation says a returning shopper wants a way back to items already opened. The criteria say the row is hidden on the first page of a session and excludes the current product. The design line says "design not supplied".

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
