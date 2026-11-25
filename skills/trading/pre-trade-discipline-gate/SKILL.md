---
name: pre-trade-discipline-gate
description: >-
  Checks a trade plan the user wrote against a local checklist and returns
  allow or block before any manual order. Use when the user asks whether a
  planned entry is allowed to go to the broker.
license: MIT
metadata:
  category: trading
  subshelf: risk
  tags: pre, trade, discipline, trading
  added: "2026-11-25"
  featured: false
  source: import
  author: TraderMonty
  authorUrl: "https://github.com/tradermonty"
  authorKind: person
  curator: Brandon
  upstream: tradermonty/claude-trading-skills
  upstreamCommit: 4080042a7863f5eeb48aabeaf60bd547efb99949
  upstreamPath: skills/pre-trade-discipline-gate/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2026 TraderMonty
---

# Pre trade discipline gate

Do this one job: a pre-trade allow or block. Adapted from `tradermonty/claude-trading-skills` at commit `4080042a7863` (MIT). Copyright (c) 2026 TraderMonty

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Read the written plan: instrument, direction, entry, stop, size, and the reason. If any of those is missing, the verdict is block. Do not invent a price or a size.
3. Block when the user says the plan is missing, the size is above the limit they stated, the idea is a revenge entry, or a regime note or circuit breaker they supplied says new risk is off.
4. Allow only when every required field is present and none of those blocks apply. Quote the line in the user's plan that satisfies each check.
5. Write the verdict as allow or block, the checks that passed, and the checks that failed. This is a note for the user to read before they type an order themselves.
6. Do not place, cancel, or route an order. Do not call a broker. Do not fetch a quote.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Plan is long ACME, entry 20, stop 18, size 1R, reason is the daily break. My rule is block revenge trades. This is not one. No circuit breaker is on.

Agent: Allow. Entry, stop, size, and reason are in the plan. Revenge and circuit breaker are clear from the note. No order is sent.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide. It does not place an order and it does not invent a price.
