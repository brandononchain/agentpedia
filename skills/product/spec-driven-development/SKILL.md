---
name: spec-driven-development
description: >-
  Creates specs before coding. Use when starting a new project, feature, or
  significant change and no specification exists yet. Use when drafting a PRD or
  requirements document with objectives and scope, or when requirements are
  unclear, ambiguous, or only exist as a vague idea. Use when a single
  requirement spans.
license: MIT
metadata:
  category: product
  subshelf: specs
  tags: spec, driven, development, product
  added: "2026-11-21"
  featured: false
  source: import
  author: Addy Osmani
  authorUrl: "https://github.com/addyosmani"
  authorKind: person
  curator: Brandon
  upstream: addyosmani/agent-skills
  upstreamCommit: 8c99fa36d90068c82d547f7c12a9d67a3e95f4ee
  upstreamPath: skills/spec-driven-development/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2025 Addy Osmani
---

# Spec driven development

Do this one job: a spec driven development. Adapted from `addyosmani/agent-skills` at commit `8c99fa36d900` (MIT). Copyright (c) 2025 Addy Osmani

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. The requirement names distinct capabilities with their own consumers or data (e.g. identity, billing, notifications, reporting)
3. Acceptance criteria cluster into groups that could ship and be verified separately
4. One capability could be cut or replaced without rewriting the others' requirements
5. Stable module ids. Kebab-case, chosen once, never renamed mid-initiative. Specs, plans, and downstream commands select work by these ids instead of guessing which spec is active.
6. Dependency direction, no cycles. Arrows point one way. If two modules each need the other, they are one module.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Draft a spec driven development from the notes in this message. Leave any figure I did not state as unknown.

Agent: A short spec driven development that uses only those notes, names the gaps, and points at the check that would show it is done.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
