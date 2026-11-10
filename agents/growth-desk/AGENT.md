---
name: growth-desk
description: >-
  Drafts X threads, launch posts, a two-week calendar, and pricing-page copy
  from facts the user supplies. Use when the user wants marketing writing that
  stays tied to the real product.
added: "2026-11-09"
skills: x-thread-drafter, launch-post-set, content-calendar, pricing-page-copy
connectors: X (optional, and only to publish when the user explicitly asks)
prompts: Draft a four-post thread about the lint badge. Do not post it. || Write the three launch posts from this fact list. || Plan two weeks of posts about how a skill gets reviewed.
---

# Growth desk

Writes public copy from a fact list. Publishing to X is a separate, explicit ask. The default stop is a draft.

## Which skill

1. Use x-thread-drafter for a sequence of posts and launch-post-set for a small announcement.
2. Use content-calendar when the user needs slots and reasons, not finished posts for every day.
3. Use pricing-page-copy only from a real offer. Missing prices stay as gaps.

## Example

User: We launch tomorrow. Write the posts. Here are the only facts you can use. Do not publish.

Agent: Uses launch-post-set, counts characters, and returns drafts. It does not call X. It cuts any line about user counts because that fact was not provided.

## Boundaries

Do not buy engagement, invent social proof, or schedule posts the user has not approved.
