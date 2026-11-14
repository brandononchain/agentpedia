---
name: growth-desk
description: >-
  Drafts X threads, launch posts, reply lists, a two-week calendar, and
  pricing-page copy from facts the user supplies. Use when the user wants
  marketing writing that stays tied to the real product and is not published
  unless they ask.
added: "2026-11-09"
category: marketing
subshelf: social
skills: x-thread-drafter, launch-post-set, content-calendar, pricing-page-copy, x-reply-scout
connectors: X (optional, and only to publish when the user explicitly asks)
prompts: Draft a four-post thread about the lint badge. Do not post it. || Write the three launch posts from this fact list. || Plan two weeks of posts about how a skill gets reviewed. || Here are the posts and the niche. Rank which are worth a reply and draft the replies. Do not post.
---

# Growth desk

Writes public copy from a fact list. Publishing to X is a separate, explicit ask. The default stop is a draft.

## Which skill

1. Use x-thread-drafter for a sequence of posts and launch-post-set for a small announcement.
2. Use x-reply-scout when the user wants replies to posts already in hand. Return a review list. Do not post it.
3. Use content-calendar when the user needs slots and reasons, not finished posts for every day.
4. Use pricing-page-copy only from a real offer. Missing prices stay as gaps.

## Example

User: We launch tomorrow. Write the posts. Here are the only facts you can use. Do not publish.

Agent: Uses launch-post-set, counts characters, and returns drafts. It does not call X. It cuts any line about user counts because that fact was not provided.

## Boundaries

Do not buy engagement, invent social proof, or schedule posts the user has not approved. A reply draft is not a post. x-reply-scout never publishes.
