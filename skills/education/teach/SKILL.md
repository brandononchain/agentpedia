---
name: teach
description: >-
  Teaches one tightly scoped concept from a goal the learner stated. Use when
  the user asks to be taught a skill or concept, wants a single lesson, or wants
  practice that checks whether they can do the thing.
license: MIT
metadata:
  category: education
  subshelf: lessons
  tags: teach, education
  added: "2026-11-24"
  featured: false
  source: import
  author: Matt Pocock
  authorUrl: "https://github.com/mattpocock"
  authorKind: person
  curator: Brandon
  upstream: mattpocock/skills
  upstreamCommit: d65391149dbb5fe76478e76fa8d5122b2aa5a70e
  upstreamPath: skills/productivity/teach/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2026 Matt Pocock
---

# Teach

Do this one job: a lesson. Adapted from `mattpocock/skills` at commit `d65391149dbb` (MIT). Copyright (c) 2026 Matt Pocock

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Restate the goal and why the learner wants it. Ask when the reason is missing. Do not invent a mission.
3. Teach one tightly scoped thing that serves that goal. Leave the next topic for a later lesson.
4. Give only the knowledge required for that skill, then a short practice that makes the learner retrieve it. Do not stop at a definition.
5. Cite a source the user supplied. When no source was supplied, label the claim uncited and ask for one. Do not present uncited material as settled.
6. Prefer a check the learner can fail: a question, a step they perform, or a recall prompt. Record what they missed.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Teach me what a pre-mortem is. I have 20 minutes and I already know a launch can fail. Do not invent a case study.

Agent: One lesson on a pre-mortem, a single retrieval question, and a note that no source was supplied so the claims stay uncited.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
