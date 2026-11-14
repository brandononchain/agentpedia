---
name: prop-firm-rule-check
description: >-
  Checks a proposed trade or day plan against prop-firm rules and account
  numbers the user supplies, then reports pass or fail with remaining headroom.
  Use when the user asks whether a trade still fits a daily loss limit, trailing
  drawdown, contract cap, news blackout, or consistency rule.
license: Apache-2.0
metadata:
  category: trading
  subshelf: risk
  tags: risk, prop
  added: "2026-11-10"
  featured: false
---

# Prop firm rule check

Check a proposed trade or a day plan against the rule card and the account numbers the user provides. Report pass or fail for each rule, the headroom left, and an overall result. This is a record of their rules. It is not an order and it is not a guess at a firm's current terms.

## Inputs

The user supplies three groups. A missing field stays missing.

- Rule card: daily loss limit, max trailing drawdown, max contracts, news blackout, and the consistency rule as they wrote it. A rule they do not provide is "not provided" and cannot pass.
- Account now: equity or balance if they gave it, loss used today, trailing drawdown already used, contracts already open, and whether the entry time sits inside a news blackout. Use their definition of drawdown. Do not pick high-water versus start-of-day for them.
- Proposal: instrument, direction, contracts or lots, and planned loss at the stop in account currency. Session time if a blackout is in the card.

## Outputs

One line per rule on the card:

- Status: pass, fail, or not checked.
- The limit, the amount already used, the amount this proposal adds, and the headroom left.
- Headroom is the limit minus what is already used minus what this proposal would add. Negative headroom is a fail.

The overall result is pass only when every rule on the card is pass. Any fail or any not-checked rule makes the overall result fail. Do not call a partial check a pass.

## Steps

1. Copy the rule card, the account numbers, and the proposal into the note. Mark every absent field as not provided. Do not fill it from memory or from a firm's public page the user did not paste.
2. Daily loss. Headroom is the daily loss limit, minus loss used today, minus planned loss at the stop. Fail if the planned loss or the limit is missing, or if headroom is below zero.
3. Trailing drawdown. Headroom is the max trailing drawdown, minus drawdown already used, minus planned loss at the stop. Fail if the stop loss, the limit, or the amount already used is missing. Do not assume which balance the firm trails from.
4. Max contracts. Headroom is the contract cap, minus contracts already open, minus the proposed size. Fail if the cap or the open size is missing, or if the sum exceeds the cap.
5. News blackout. Pass only when the user says the entry is outside the blackout. Fail when they say it is inside. Not checked when they did not say, and the overall result then fails.
6. Consistency. Apply only the formula the user wrote, with the numbers they gave. If they named the rule but not the formula or the figures, mark it not checked. Do not invent a percentage.
7. Validate the note against the inputs. Every limit and every account number must trace to the user. Delete a figure that does not. State the overall pass or fail in one line. Do not place, modify, or close an order.

## Example

User: Daily loss limit 500, loss used today 200. Max contracts 3, none open. Proposal is 2 NQ contracts with 250 of planned loss at the stop. They did not give drawdown, a news status, or a consistency formula. Do not send an order.

Agent: Daily loss passes. Headroom is 50, from 500 minus 200 minus 250. Contracts pass. Headroom is 1, from 3 minus 0 minus 2. Trailing drawdown, news blackout, and consistency are not checked, because those inputs were not provided. Overall result: fail. The two passing rules are not an overall pass. No order is sent.

## Guardrails

Do not invent a firm's rule, a price, a fill, or an account balance. Do not tell the user to take the trade. Do not raise a limit to make the check pass. Do not send an order to a terminal. This check is not investment advice and it is not a promise the firm will agree with the arithmetic.
