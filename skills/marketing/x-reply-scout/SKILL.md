---
name: x-reply-scout
description: >-
  Ranks recent posts worth replying to for a niche and drafts short, specific
  replies for a person to review. Use when the user gives target accounts or
  keywords and wants a reply list rather than a post published for them.
license: Apache-2.0
metadata:
  category: marketing
  subshelf: social
  tags: x, replies
  added: "2026-11-10"
  featured: false
---

# X reply scout

Build a review list of recent posts worth a reply, and a draft reply for each one. The user decides what gets posted. This skill stops at the list.

## Inputs

- The niche, in one sentence.
- Target accounts, keywords, or both, as the user named them.
- The posts in hand: author, text, time, and any public counts the user or a connector actually returned. A link is optional.
- Voice notes, if the user gave them. If they did not, write plain and specific.

## Outputs

A ranked review list, nothing published.

- Kept rows: rank, author, why this post is worth a reply, the draft reply, the character count, and the fact the reply depends on.
- Skipped rows: the post and the reason (off niche, no new angle, or it would require a claim the user did not verify).
- Missing data called out as "not supplied," including likes, replies, and follower counts that were not in the input.

## Steps

1. Restate the niche and the accounts or keywords. If no posts were supplied and no connector returned any, stop and ask. Do not invent posts, timestamps, or counts.
2. Keep a post only when it is on the niche and the user could add a specific detail from the post itself. Prefer posts the user marked as fresh or rising. If they did not supply a count or a time, do not guess that the post is rising.
3. Skip posts that are off niche, that only invite a generic compliment, or that would require a personal fact, a metric, or a relationship the user did not verify.
4. Draft one reply per kept post. Keep it at or under 280 characters. Tie it to a concrete line in that post. No "great post," no follow-bait, and no tag the user did not name.
5. Validate the list before showing it. Every cited post was in the input. Every draft is 280 characters or fewer, and the count is written next to it. No reply was published. Show the kept rows and the skipped rows, then wait.

## Example

User: Niche is linted agent skills. Keywords are SKILL.md and skill smell. Posts supplied: one from a maintainer asking how people review skills before sharing them, posted this morning, no like count; one from a meme account with no text about skills. Do not post.

Agent: Keeps the maintainer post because it asks the review question the niche can answer. Draft, 148 characters: "We run a linter before a skill is listed. The usual failures are a description that never says when to use it, and no example. Happy to show the rule list." Then it deletes that draft, because "we" claims a practice the user did not state in this request, and rewrites to: "The check I would want first: the description says when to use the skill, and there is one real example. What do you reject on sight?" That second draft is the one on the list, with its character count. The meme post is skipped as off niche. Likes are marked not supplied. Nothing is posted.

## Guardrails

Do not post, like, repost, follow, or send a message. Do not invent a follower count, a view count, or a quote. Do not pretend the user read a thread that was not supplied. A draft the user has not accepted stays a draft.
