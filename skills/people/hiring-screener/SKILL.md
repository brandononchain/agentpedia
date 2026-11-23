---
name: hiring-screener
description: >-
  Takes a pile of applications and turns it into a ranked shortlist, scored only
  against the job's stated rubric, with drafted replies to every candidate,
  scheduled interviews, and an onboarding checklist for whoever gets hired.
  Picks up where job-post-builder leaves off and carries the funnel through to
  first day. Use when the user asks for a hiring screener.
license: Apache-2.0
metadata:
  category: people
  subshelf: interviews
  tags: hiring, screener, people
  added: "2026-11-23"
  featured: false
  source: import
  author: Anthropic
  authorUrl: "https://github.com/anthropics"
  authorKind: organization
  curator: Brandon
  upstream: anthropics/knowledge-work-plugins
  upstreamCommit: 2baf6d1eded3cd7aeff0b5c5918601a5799189b4
  upstreamPath: small-business/skills/hiring-screener/SKILL.md
  upstreamLicense: Apache-2.0
  copyright: Copyright Anthropic
---

# Hiring screener

Do this one job: a hiring screener. Adapted from `anthropics/knowledge-work-plugins` at commit `2baf6d1eded3` (Apache-2.0). Copyright Anthropic

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. The rubric from job-post-builder, if that ran
3. The job post itself, from Drive, M365, Gmail, or uploaded
4. Built with the owner now, from the post — takes five minutes
5. Gmail — the hiring inbox, with attachments
6. Uploaded files — resumes, applications, cover letters. The common path
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Draft a hiring screener from the notes in this message. Leave any figure I did not state as unknown.

Agent: A short hiring screener that uses only those notes, names the gaps, and points at the check that would show it is done.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
