---
name: content-calendar
description: >-
  Builds a two-week content calendar from one theme, with a channel, a topic,
  and a reason for each slot. Use when the user asks for a posting calendar or a
  content plan.
license: Apache-2.0
metadata:
  category: marketing
  tags: calendar, x
  added: "2026-11-09"
  featured: false
---

# Content calendar

Plan two weeks from one theme. Every slot needs a reason tied to the theme. Empty days are allowed. A calendar full of posts with nothing to say is a failed calendar.

## Steps

1. Confirm the theme, the channels, the start date, and how many posts the user is willing to publish. Default to X only and four posts across ten weekdays if they do not specify.
2. Propose slots. Each slot has a date, a channel, a one-line topic, and the job of that post (teach, show a specimen, or point at the repo).
3. Leave days blank rather than repeating the same claim.
4. Note what source material each slot needs, so the user can see which posts are blocked on a fact.
5. Validate the calendar: it covers the agreed length, it stays on the theme, and it does not exceed the volume the user accepted. Present it as a draft.

## Example

User: Theme is "how Agentpedia lints skills." Start Monday 16 Nov 2026. X only. Four posts.

Agent: Mon 16 — what a lint error blocks. Wed 18 — a walk through one clean skill's badge. Fri 20 — the rules that catch secrets and piped installs. Tue 24 — how to add a skill. Other weekdays stay empty. Each slot lists the rule page or the skill it will show.

## Boundaries

Do not schedule posts that require invented customer stories. Do not fill a weekend unless the user posts then.
