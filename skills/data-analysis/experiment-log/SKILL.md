---
name: experiment-log
description: >-
  Records a hypothesis, the observed result, and a decision to ship, iterate, or
  stop. Use when the user asks to log an experiment, write up an A/B test, or
  capture a learning.
license: Apache-2.0
metadata:
  category: data-analysis
  tags: experiments, data
  added: "2026-11-06"
  featured: false
---

# Experiment log

Write an experiment entry that a teammate can audit later. Separate what was predicted, what was measured, and what will be done.

## Steps

1. Record the hypothesis, the audience, the start and end, and the primary metric. Use the metric name the user used.
2. Record the result with the comparison (control and variant), the unit count, and the direction. If uncertainty or a sample-size note was supplied, include it. If it was not, write "not provided."
3. State the decision: ship, iterate, or stop. The decision must follow from the result the user reported, not from a preferred outcome.
4. Add one learning that would change the next test, and one thing this test does not prove.
5. Validate the entry: hypothesis, result, and decision are three separate sections, and no number appears that the user did not supply.

## Example

User: Hypothesis: shorter onboarding increases activation. Control 20%, variant 24%, 800 workspaces each, two weeks. We want to ship.

Agent: Result — variant 24% versus control 20% on 800 workspaces per arm. Uncertainty was not provided. Decision — ship, because that is the call the user made on a positive primary metric. Does not prove the gain holds past two weeks.

## Boundaries

Do not compute a significance claim from counts alone. Do not upgrade "iterate" into "ship."
