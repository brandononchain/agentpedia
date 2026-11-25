---
name: x-twitter-growth
description: >-
  Drafts an X profile critique and a one-week post list from the bio, pinned
  post, and recent posts the user pastes. Use when the user asks for an X or
  Twitter growth plan and does not want it posted.
license: MIT
metadata:
  category: marketing
  subshelf: social
  tags: x, twitter, growth, marketing
  added: "2026-11-25"
  featured: false
  source: import
  author: Alireza Rezvani
  authorUrl: "https://github.com/alirezarezvani"
  authorKind: person
  curator: Brandon
  upstream: alirezarezvani/claude-skills
  upstreamCommit: 91a20bafbdba2d03be133b7bf55571ceeeade638
  upstreamPath: marketing-skill/skills/x-twitter-growth/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2025 Alireza Rezvani
---

# X twitter growth

Do this one job: an X growth draft. Adapted from `alirezarezvani/claude-skills` at commit `91a20bafbdba` (MIT). Copyright (c) 2025 Alireza Rezvani

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Read only the bio, pinned post, and recent posts the user pasted, plus the niche and the offer they named. If a follower count or a proof point is missing, label it unknown. Do not invent one.
3. Critique what was pasted: a missing value line, a vague niche, a hashtag in the bio, a pinned post with no ask, or a gap the paste does not cover. Skip a check the user did not provide text for.
4. Draft a revised bio and a pinned post. Include social proof only when the user supplied the fact. Put a link in a reply draft only when the user gave the link.
5. Draft a one-week list in the user's voice: one thread outline, a few short posts, and replies they could send. Each item cites a fact from the paste. Do not add a claim, a metric, or a customer that was not supplied.
6. Show the draft and wait. Do not post, follow, like, or scrape an account.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Bio is "builder | thinker". Pinned post is two years old and has no ask. Niche is a CLI for changelog drafts. Offer is a waitlist at example.com. Do not invent follower counts.

Agent: A bio that names the CLI and the waitlist, a pinned post with an ask, and a one-week list about changelog drafts. Follower count stays unknown. Nothing is posted.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide. It does not post to X and it does not scrape accounts.
