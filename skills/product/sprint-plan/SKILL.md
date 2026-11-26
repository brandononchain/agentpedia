---
name: sprint-plan
description: >-
  Plans one sprint from the capacity, velocity, and backlog the user supplies.
  Use when the user asks for a sprint plan, a capacity check, or which stories
  fit the next sprint.
license: MIT
metadata:
  category: product
  subshelf: roadmaps
  tags: sprint, plan, product
  added: "2026-11-26"
  featured: false
  source: import
  author: Pawel Huryn
  authorUrl: "https://github.com/phuryn"
  authorKind: person
  curator: Brandon
  upstream: phuryn/pm-skills
  upstreamCommit: 9af7bfd0bc47fdad43c2eaa7a43cd13918e7aaef
  upstreamPath: pm-execution/skills/sprint-plan/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2026 Pawel Huryn
---

# Sprint plan

Do this one job: a sprint plan. Adapted from `phuryn/pm-skills` at commit `9af7bfd0bc47` (MIT). Copyright (c) 2026 Pawel Huryn

## Steps

1. Confirm sprint length, who is available, the velocity the user states, and the buffer they want held back. If velocity is missing, ask. Do not invent a velocity or a buffer.
2. Capacity is the stated velocity minus the buffer. Note anyone the user said is out, and do not assign them a story.
3. Take stories in the order the user ranked them. Stop when the points reach capacity. Flag a story that has no acceptance criteria and leave it out of the commitment.
4. List only the dependencies the user named, in the order those dependencies force.
5. Write the sprint goal as one sentence in the user's words. Validate that committed points do not exceed the capacity just computed.

## Example

User: Two weeks. Velocity is 20 points. Hold back 4. Ada is out. Ranked stories are login fix (5), export (8), and billing (13). Export depends on the login fix. No acceptance criteria on billing.

Agent: Capacity is 16. The plan commits the login fix then export (13 points) and leaves billing out because it has no acceptance criteria and would pass 16. Ada has no story. The goal uses the user's words for the login fix and the export.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
