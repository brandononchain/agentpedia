---
name: meeting-decisions
description: >-
  Extracts decisions, owners, and open questions from meeting notes. Use when
  the user asks for meeting notes, action items, or a decision log.
license: Apache-2.0
metadata:
  category: productivity
  subshelf: meetings
  tags: meetings
  added: "2026-11-05"
  featured: false
---

# Meeting decisions

Extract what was decided, who owns the next action, and what stayed open. A discussion is not a decision until the notes say a choice was made.

## Steps

1. Read the notes, the date, and the attendees if provided.
2. List decisions as complete sentences. If the notes only show options, put those under open questions, not decisions.
3. List actions with an owner and a due date when the notes include them. If the owner is missing, write "owner not named" rather than assigning someone.
4. List open questions that block a decision.
5. Validate each item against a line in the notes. Drop anything that was only implied. Keep the result shorter than the notes.

## Example

User notes: "We argued about SQLite versus a generated JSON file. Jordan said generate the JSON in CI. Nobody disagreed out loud. Priya will draft the schema tomorrow. Still unclear who publishes the site."

Agent: Decision — generate the JSON in CI (Jordan stated it; the notes do not record an explicit vote). Action — Priya drafts the schema, due tomorrow. Open — who publishes the site. The argument itself is not listed as a second decision.

## Boundaries

Do not assign an owner who was not in the notes. Do not email the notes to attendees unless the user asks.
