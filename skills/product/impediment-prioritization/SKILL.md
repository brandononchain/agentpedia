---
name: impediment-prioritization
description: >-
  Ranks any list of impediments and their countermeasures using a value-stream
  scoring model (ROI, Cost to Implement, Ease of Deployment, Risk Factor) and a
  fixed prioritization formula. Use when someone asks to prioritize, rank,
  sequence, or triage impediments, countermeasures, remediation items, risks,
  findings.
license: MIT
metadata:
  category: product
  subshelf: specs
  tags: impediment, prioritization, product
  added: "2026-11-23"
  featured: false
  source: import
  author: ajenns
  authorUrl: "https://github.com/github"
  authorKind: organization
  curator: Brandon
  upstream: github/awesome-copilot
  upstreamCommit: f10fdb8b2660ce85c98f220b2f1ca24653768a5c
  upstreamPath: skills/impediment-prioritization/SKILL.md
  upstreamLicense: MIT
  copyright: "Copyright GitHub, Inc."
---

# Impediment prioritization

Do this one job: an impediment prioritization. Adapted from `github/awesome-copilot` at commit `f10fdb8b2660` (MIT). Copyright GitHub, Inc.

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Ingest the impediment list. Confirm 1:1 impediment-to-countermeasure mapping; collapse duplicates.
3. Confirm the countermeasure for each impediment. Prefer documented best practice for the domain. Cite a public / authoritative link when one is available.
4. Score all four criteria using the rubric. Write a one-line rationale per criterion.
5. Compute Priority using the formula. Round to one decimal place.
6. Sort rows by Priority descending. Assign Rank starting at 1.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Draft an impediment prioritization from the notes in this message. Leave any figure I did not state as unknown.

Agent: A short impediment prioritization that uses only those notes, names the gaps, and points at the check that would show it is done.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
