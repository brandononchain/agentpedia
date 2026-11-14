---
name: session-plan
description: >-
  Writes a trading session plan with a bias, an invalidation, a max loss, and a
  time to stop. Use when the user asks for a plan before the session opens or
  for a checklist before they trade.
license: Apache-2.0
metadata:
  category: trading
  subshelf: execution
  tags: planning, risk
  added: "2026-11-09"
  featured: false
---

# Session plan

Write the plan before the session, from the limits the user chooses. The plan constrains trading. It does not pick trades, and it does not override a max loss.

## Steps

1. Record the session window, the symbols in play, and the account. Use the symbols the user named.
2. Write the bias only if the user stated one. Otherwise write "no bias stated."
3. Record invalidation (what would prove the bias wrong), max loss in account currency, and the clock time after which no new trade is allowed. If max loss is missing, stop and ask. Do not invent a number.
4. Add a stop-trading rule: hit the max loss, hit the clock, or two unplanned deviations, whichever comes first.
5. Validate the plan: it has a max loss, a stop time, and no order. Show it and wait for the user to accept it. Do not place trades from this skill.

## Example

User: London session, EURUSD only, max loss 100, no new trades after 11:30 UTC. No bias yet.

Agent: Symbols: EURUSD. Bias: not stated. Invalidation: not set, because there is no bias. Max loss: 100 account currency. No new trade after 11:30 UTC. Stop also if two trades break the written plan. Nothing is sent to the terminal.

## Boundaries

Do not raise the max loss mid-plan. Do not convert the plan into entries and targets unless the user asks, and even then keep the max loss.
