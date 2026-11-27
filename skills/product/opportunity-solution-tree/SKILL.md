---
name: opportunity-solution-tree
description: >-
  Builds an opportunity solution tree from an outcome and research the user
  supplies. Use when the user asks to map opportunities, solutions, and
  experiments before deciding what to build.
license: MIT
metadata:
  category: product
  subshelf: discovery
  tags: opportunity, solution, tree, product
  added: "2026-11-27"
  featured: false
  source: import
  author: Pawel Huryn
  authorUrl: "https://github.com/phuryn"
  authorKind: person
  curator: Brandon
  upstream: phuryn/pm-skills
  upstreamCommit: 9af7bfd0bc47fdad43c2eaa7a43cd13918e7aaef
  upstreamPath: pm-product-discovery/skills/opportunity-solution-tree/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2026 Pawel Huryn
---

# Opportunity solution tree

Do this one job: an opportunity solution tree from research the user supplies. Adapted from `phuryn/pm-skills` at commit `9af7bfd0bc47` (MIT). Copyright (c) 2026 Pawel Huryn

## Steps

1. Take the outcome from the user. If they did not state a metric, write "outcome not measured" and do not invent a target.
2. List opportunities only from the research they pasted. Use the customer's words when a quote is there. If there is no research, stop and ask.
3. If they supplied importance and satisfaction as numbers from 0 to 1, the opportunity score is importance times one minus satisfaction. If they did not, leave the score unknown.
4. For the opportunities they asked to pursue, list solutions they named. A solution they did not already choose is labeled a proposal.
5. For a test they asked for, write the hypothesis, method, metric, and success line only where they supplied them. Leave the rest unknown.
6. Check the tree. No opportunity without a source line, and no percentage that was not in the notes.

## Example

User: Outcome is "more teams finish setup," no target number. Four interviews said the invite step fails. Importance 0.9 and satisfaction 0.2 came from those interviews. I have not picked a solution.

Agent: Outcome — more teams finish setup; target unknown. Opportunity — invite step fails (four interviews); score 0.9 times 0.8 = 0.72. Solutions — none chosen; no proposal added until you ask. Experiment — unknown. No other opportunities invented.

## Boundaries

Do not publish the tree or turn a proposal into a committed roadmap. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent customers, scores, or success thresholds.
