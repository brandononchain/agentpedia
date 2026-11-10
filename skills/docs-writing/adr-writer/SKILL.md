---
name: adr-writer
description: >-
  Writes an architecture decision record with context, the decision, and
  consequences. Use when the user asks to record a technical decision, start an
  ADR, or explain why an approach was chosen.
license: Apache-2.0
metadata:
  category: docs-writing
  tags: adr, docs
  added: "2026-11-07"
  featured: false
---

# ADR writer

Record one decision so a later reader can see what was chosen and what was rejected. Use the skeleton in [references/madr-skeleton.md](references/madr-skeleton.md). One decision per record.

## Steps

1. Confirm the decision title, the status (proposed, accepted, or superseded), and the date. Ask if the status is unclear.
2. Write the context as the forces in play, not a history of meetings.
3. State the decision in a few sentences that a reviewer can implement. List the options that were rejected and why, using only options the user actually considered.
4. Write consequences: what becomes easier, what becomes harder, and what follow-up work exists.
5. Validate the record: it names one decision, it does not contradict the context, and it does not claim a consensus the user did not state.

## Example

User: Record the decision to keep the catalog as static JSON generated at build time, not a database. Status accepted. Date 2026-11-10.

Agent: Context — the directory is small and must be reviewable in git. Decision — generate `data/catalog.json` during build. Rejected — a hosted database, because it adds a credential and a service the site does not need. Consequence — content edits are commits, and the site cannot show a skill that has not been rebuilt.

## Boundaries

Do not invent stakeholders or vote counts. Do not expand one ADR to cover unrelated decisions.
