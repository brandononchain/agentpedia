---
name: summarize-interview
description: >-
  Summarize a customer interview transcript into a structured template with
  JTBD, satisfaction signals, and action items. Use when processing interview
  recordings or transcripts, synthesizing discovery interviews, or creating
  interview summaries
license: MIT
metadata:
  category: people
  subshelf: interviews
  tags: summarize, interview, people
  added: "2026-11-24"
  featured: false
  source: import
  author: Pawel Huryn
  authorUrl: "https://github.com/phuryn"
  authorKind: person
  curator: Brandon
  upstream: phuryn/pm-skills
  upstreamCommit: 9af7bfd0bc47fdad43c2eaa7a43cd13918e7aaef
  upstreamPath: pm-product-discovery/skills/summarize-interview/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2026 Pawel Huryn
---

# Summarize interview

Do this one job: a summarize interview. Adapted from `phuryn/pm-skills` at commit `9af7bfd0bc47` (MIT). Copyright (c) 2026 Pawel Huryn

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Read the full transcript the user supplied before writing.
3. Record the date, participants, and background only when the transcript states them. Use a dash when a field is absent.
4. State the current solution, what the customer likes, the job to be done, the satisfaction signal, and the action items.
5. Use the customer's words for jobs and pains. Do not add a quote that is not in the transcript.
6. Keep the summary in plain language a non-specialist can read.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Draft a summarize interview from the notes in this message. Leave any figure I did not state as unknown.

Agent: A short summarize interview that uses only those notes, names the gaps, and points at the check that would show it is done.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
