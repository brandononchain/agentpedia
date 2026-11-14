---
name: market-data-briefing
description: >-
  Writes a pre-session market briefing from quotes and headlines the user or a
  data connector supplies. Use when the user asks for a morning brief, a session
  outlook, or a note on what the market just did.
license: Apache-2.0
compatibility: >-
  Uses quotes the user pastes or a market-data connector they have authorized.
  Does not send orders.
metadata:
  category: trading
  subshelf: research
  tags: markets, briefing
  added: "2026-11-10"
  featured: false
---

# Market data briefing

Write a briefing from numbers and headlines in hand. The field list is in [references/briefing-fields.md](references/briefing-fields.md). If a quote is missing, say it is missing. Never invent a price, a percentage, or a headline.

## Steps

1. Record the session, the timezone, and the as-of time for the data.
2. For each symbol the user named, write last, the change versus the reference they gave (prior close or session open), and the source (pasted quote or a named connector). Skip any symbol with no quote.
3. List headlines the user supplied or a connector returned, each with its source. Do not add headlines from memory.
4. Write three lines: what changed, what level the user said matters, and what is unknown. Do not turn that into a trade instruction.
5. Validate every number and headline against the inputs. Delete anything you cannot trace. Do not place orders or tell the user they should buy or sell.

## Example

User: Pre-London brief. EURUSD last 1.0862, prior close 1.0840, source their paste at 06:50 UTC. No headline provided. They care about 1.0900.

Agent: As of 06:50 UTC, EURUSD is 1.0862, up 0.0022 versus the prior close they supplied. No headline was provided. The level they named is 1.0900, which price has not reached in this note. Unknown: why it moved. No trade is recommended.

## Boundaries

A briefing is a record of supplied data. It is not a signal service, and it does not forecast a close.
