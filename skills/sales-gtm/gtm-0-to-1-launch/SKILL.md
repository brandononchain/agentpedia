---
name: gtm-0-to-1-launch
description: >-
  Writes a 0-to-1 launch plan that names where adoption stalls and the next
  experiment. Use when the user asks how to find the first customers or why a
  launch is not converting.
license: MIT
metadata:
  category: sales-gtm
  subshelf: outbound
  tags: gtm, launch, sales
  added: "2026-11-26"
  featured: false
  source: import
  author: "Smit Patel (https://linkedin.com/in/smitkpatel)"
  authorUrl: "https://github.com/github"
  authorKind: organization
  curator: Brandon
  upstream: github/awesome-copilot
  upstreamCommit: 93fc8b9ee3ef56b9b5e7261e6ce92d314cb2c1cf
  upstreamPath: skills/gtm-0-to-1-launch/SKILL.md
  upstreamLicense: MIT
  copyright: "Copyright GitHub, Inc."
---

# Gtm 0 to 1 launch

Do this one job: a 0-to-1 launch plan. Adapted from `github/awesome-copilot` at commit `93fc8b9ee3ef` (MIT). Copyright GitHub, Inc.

## Steps

1. Confirm the product, who the first customer is, and the counts the user has (visits, signups, replies, or trials). A missing count stays unknown. Do not invent one.
2. Place the stall in one layer, using only that evidence. Positioning: buyers treat it as the same as something else. Experience: people arrive and do not activate. Distribution: the people who need it never see it.
3. Draft one two-week experiment that changes only that layer. The offer and the audience must be facts the user stated.
4. State the result that would keep the experiment and the result that would stop it. If the user set no threshold, ask. Do not pick a number for them.
5. Validate that no impression count, signup count, or press mention appears unless the user supplied it.

## Example

User: The API docs product has 40 trial signups and 2 activated accounts. The people who sign up do not finish the first call. The audience is backend engineers at small companies.

Agent: The stall is experience, because the user supplied signups and activations and the gap is between them. The experiment is a two-week concierge setup for backend engineers at small companies, using the offer the user already stated. The stop/keep line asks the user for a threshold. The counts in the plan are 40 and 2.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
