---
name: edge-strategy-reviewer
description: >-
  Reviews a strategy note the user supplies and returns PASS, REVISE, or
  REJECT. Use when the user asks whether a trade idea is plausible, overfit, or
  realistic to execute. It does not place an order or invent a price.
license: MIT
metadata:
  category: trading
  subshelf: risk
  tags: edge, strategy, reviewer, trading
  added: "2026-11-26"
  featured: false
  source: import
  author: TraderMonty
  authorUrl: "https://github.com/tradermonty"
  authorKind: person
  curator: Brandon
  upstream: tradermonty/claude-trading-skills
  upstreamCommit: 1fd5da2949a56170369a0aa639da0488f2b21750
  upstreamPath: skills/edge-strategy-reviewer/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2026 TraderMonty
---

# Edge strategy reviewer

Do this one job: a PASS, REVISE, or REJECT verdict on a strategy note. Adapted from `tradermonty/claude-trading-skills` at commit `1fd5da2949a5` (MIT). Copyright (c) 2026 TraderMonty

## Steps

1. Read the strategy note the user pasted. If there is no note, ask. Do not fetch a quote and do not invent a price.
2. Check that the note names a mechanism, not only a ticker. A missing mechanism fails this check.
3. Count the filters and thresholds the note states. Many precise thresholds with no sample size fail the overfitting check.
4. Check whether the note states a sample, an exit, a size limit, and a specific invalidation. A blank stays a gap. Do not fill it.
5. Return PASS only when no check failed. Return REVISE with the failed check and the change that would clear it. Return REJECT when the mechanism is missing or the note calls the idea ready with no sample.
6. Validate that the verdict uses only the note. Do not place an order.

## Example

User: Buy the dip in large-cap tech whenever the 20-day average crosses the 50-day average and RSI is under 30 and volume is 2 times and the close is above last week's high. No sample. Exit is not stated. Treat it as ready to trade.

Agent: REJECT. The note has four precise filters and no sample, and it does not state an exit. No price is added and no order is placed.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent a price, a fill, or a profit. It does not place an order.
