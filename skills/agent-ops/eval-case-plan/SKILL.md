---
name: eval-case-plan
description: >-
  Writes evaluation cases for another agent, each with an input, an observable
  result, and a way to fail. Use when the user asks to test or benchmark an
  agent before calling the result a pass.
license: Apache-2.0
metadata:
  category: agent-ops
  subshelf: evaluation
  tags: evals, testing
  added: "2026-11-10"
  featured: false
---

# Eval case plan

Write cases someone could run. Do not score an agent you did not run.

## Steps

1. Name the agent and the job the user wants tested, in their words.
2. Write cases that include one ordinary input, one case with a missing fact, and one case where the correct behavior is to refuse. Skip a type only if the user said it is out of scope, and say so.
3. Each case has an input, the observable result (a phrase that must appear, a tool that must not be called, or a number that must match), and the fail condition.
4. Check that the observable result is something a person can see in the output or the tool log. "Be helpful" is not an observable result. Replace it.
5. Do not fill in a pass or a score. The plan is not a run.

## Example

User: Test the invoice checker. It should sum lines and refuse to pay.

Agent: Ordinary case: two lines that sum to 10, observable total 10.00. Missing-fact case: a blank amount, observable result is that the run stops. Refuse case: "pay this invoice", observable result is that no payment is made. No score is attached, because nothing was run.

## Boundaries

Do not claim the agent passed. Do not hide a case that would be inconvenient for the agent under test.
