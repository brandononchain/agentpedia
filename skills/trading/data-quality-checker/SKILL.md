---
name: data-quality-checker
description: >-
  Checks a market note the user supplies for scale, ticker notation, dates,
  allocation totals, and units. Use when the user asks to review a market
  write-up before they publish it.
license: MIT
metadata:
  category: trading
  subshelf: research
  tags: data, quality, checker, trading
  added: "2026-11-27"
  featured: false
  source: import
  author: TraderMonty
  authorUrl: "https://github.com/tradermonty"
  authorKind: person
  curator: Brandon
  upstream: tradermonty/claude-trading-skills
  upstreamCommit: 7c3c959a23b1d409929d50c7ba7b6dc4d40abdf8
  upstreamPath: skills/data-quality-checker/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2026 TraderMonty
---

# Data quality checker

Do this one job: a review of one market note the user pasted. Adapted from `tradermonty/claude-trading-skills` at commit `7c3c959a23b1` (MIT). Copyright (c) 2026 TraderMonty

## Steps

1. Read the note. Do not fetch a price or a page. Do not place an order. Do not run a script.
2. Flag a price whose unit or scale disagrees with another line about the same instrument in the note. Do not replace it with a live quote.
3. Flag a ticker or name spelled two ways, and a date whose weekday does not match the calendar.
4. Sum percentages the note presents as one book. If they are not about 100, report the total and the gap. Ignore percentages that are not allocations.
5. Flag a unit that switches without a conversion the note itself shows, including basis points and percent.
6. Write each finding as advisory: the line, the check, and what would resolve it. Check that every finding points at a line in the note.

## Example

User note: "GLD at $2,800 on Monday, January 1, 2026. Book: GLD 60%, TLT 50%."

Agent: Advisory. January 1, 2026 was a Thursday, not a Monday. The book sums to 110%, gap 10 points. The $2,800 figure is not compared with a second GLD line in the note, so the scale is not flagged. No price was looked up and no order was drafted.

## Boundaries

Do not publish the note, send an order, or correct a price from memory. Show the findings and wait. Do not install packages or phone a vendor. This skill does not invent a quote, a fill, or a target.
