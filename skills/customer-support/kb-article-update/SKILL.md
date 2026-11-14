---
name: kb-article-update
description: >-
  Updates a knowledge-base article from the current article and the tickets
  that show it is wrong or thin. Use when the user asks to fix a help article
  after the same question keeps arriving.
license: Apache-2.0
metadata:
  category: customer-support
  subshelf: knowledge
  tags: knowledge-base, support
  added: "2026-11-10"
  featured: false
---

# Knowledge-base update

Change an article the user already has, using tickets they also paste. Do not publish it.

## Steps

1. Quote the part of the article the tickets contradict or leave incomplete. If the tickets do not touch the article, say no update is supported.
2. Write the replacement sentences. Each new fact must appear in a ticket or in a policy the user pasted with them.
3. Keep the article's existing scope. Do not add a product area the old article did not cover unless a ticket forces a one-line pointer and the user asked for that pointer.
4. Check the draft against the tickets: a sentence a ticket does not support is removed.
5. List what you did not change. Hand it back for the user to publish.

## Example

User: Article says "Exports are CSV only." Three tickets from this week say the button now offers CSV and JSON, and they pasted the release note that says the same.

Agent: Replaces that sentence with CSV and JSON, and cites the release note they pasted. The rest of the article is unchanged. The draft is not published.

## Boundaries

Do not invent a feature to make the article sound complete, and do not delete a warning the tickets did not address.
