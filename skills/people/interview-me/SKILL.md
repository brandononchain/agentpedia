---
name: interview-me
description: >-
  Extracts what the user actually wants instead of what they think they should
  want. Achieves this through one-question-at-a-time interview until ~95%
  confidence about the underlying intent. Use when an ask is underspecified
  ("build me X" without "for whom" or "why now"), when the user explicitly
  invokes ("interview.
license: MIT
metadata:
  category: people
  subshelf: interviews
  tags: interview, me, people
  added: "2026-11-21"
  featured: false
  source: import
  author: Addy Osmani
  authorUrl: "https://github.com/addyosmani"
  authorKind: person
  curator: Brandon
  upstream: addyosmani/agent-skills
  upstreamCommit: 8c99fa36d90068c82d547f7c12a9d67a3e95f4ee
  upstreamPath: skills/interview-me/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2025 Addy Osmani
---

# Interview me

Do this one job: an interview me. Adapted from `addyosmani/agent-skills` at commit `8c99fa36d900` (MIT). Copyright (c) 2025 Addy Osmani

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. The user can't react to your hypotheses if you bury them in a list
3. Batches encourage skim-reading and surface answers
4. The third question often depends on the answer to the first; asking them all at once locks in the wrong framing
5. The user's energy for thinking carefully is finite; spend it one question at a time
6. The user reacts faster to a wrong guess than they generate an answer from scratch
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Use the case below as the source material for an interview me.

A short before-and-after. **Without `interview-me`:** The agent has assumed: who it's for, what metrics, what "for our team" means, what success looks like. None of these are stated. Every assumption is a place the user can later say "that's not what I meant." **With `interview-me`:**

Agent: A draft that keeps those facts and leaves out anything the case did not state.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
