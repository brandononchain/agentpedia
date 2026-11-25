---
name: devrel-hiring
description: >-
  Writes a DevRel role scorecard and job posting from the company type, the
  role, and the funding driver the user states. Use when the user asks how to
  hire a developer advocate or to draft a DevRel posting.
license: MIT
metadata:
  category: people
  subshelf: roles
  tags: devrel, hiring, people
  added: "2026-11-25"
  featured: false
  source: import
  author: Samuel Berthe
  authorUrl: "https://github.com/samber"
  authorKind: person
  curator: Brandon
  upstream: samber/developer-relations-skills
  upstreamCommit: bc8ac6d8fbcceda4334222ec997ff3113d0f48aa
  upstreamPath: skills/devrel-hiring/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2026 Samuel Berthe
---

# Devrel hiring

Do this one job: a DevRel scorecard and posting. Adapted from `samber/developer-relations-skills` at commit `bc8ac6d8fbcc` (MIT). Copyright (c) 2026 Samuel Berthe

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Ask, one at a time, for anything still missing: company type (early startup, growth, big tech, or OSS foundation), the role target, what funds the role, and whether the bar is shipping samples or public communication. Stop when those four are known.
3. State the role in one sentence the user can veto. A startup generalist, a big-tech advocate, and an OSS role do not share a posting. Do not copy a template across them.
4. Write a one-sentence mission that names the funding driver the user stated.
5. Write three to eight outcomes. Quantify one only when the user supplied the number. Leave the quantity blank rather than inventing a target.
6. List five to seven competencies for that company type. Flag a requirement that does not connect to an outcome.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: First DevRel hire at a seed startup. The role is funded to get developers to try the API. They should ship SDK samples. Do not invent a salary or a headcount.

Agent: A scorecard whose mission is developer adoption of the API, with outcomes left unquantified, and a note that salary and headcount were not supplied.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide. It writes the posting and the scorecard. It does not rank candidates, design an interview loop, or store a memory file.
