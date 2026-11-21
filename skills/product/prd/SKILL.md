---
name: prd
description: >-
  Generate high-quality Product Requirements Documents (PRDs) for software
  systems and AI-powered features. Includes executive summaries, user stories,
  technical specifications, and risk analysis. Use when the user asks for a prd.
license: MIT
metadata:
  category: product
  subshelf: specs
  tags: prd, product
  added: "2026-11-21"
  featured: false
  source: import
  author: "GitHub, Inc."
  authorUrl: "https://github.com/github"
  authorKind: organization
  curator: Brandon
  upstream: github/awesome-copilot
  upstreamCommit: f10fdb8b2660ce85c98f220b2f1ca24653768a5c
  upstreamPath: skills/prd/SKILL.md
  upstreamLicense: MIT
  copyright: "Copyright GitHub, Inc."
---

# Prd

Do this one job: a prd. Adapted from `github/awesome-copilot` at commit `f10fdb8b2660` (MIT). Copyright GitHub, Inc.

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. The Core Problem: Why are we building this now?
3. Success Metrics: How do we know it worked?
4. Constraints: Budget, tech stack, or deadline?
5. Define Non-Goals to protect the timeline.
6. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Use the case below as the source material for a prd.

**Problem**: Users struggle to find specific documentation snippets in massive repositories. **Solution**: An intelligent search system that provides direct answers with source citations. **Success**: - Reduce search time by 50%.

Agent: A draft that keeps those facts and leaves out anything the case did not state.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
