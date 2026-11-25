---
name: ab-test-analysis
description: >-
  Reads an A/B test the user already ran and reports lift, whether the sample
  and the window support a call, and a ship, extend, or stop recommendation.
  Use when the user asks to read experiment results or decide if a variant
  should ship.
license: MIT
metadata:
  category: product
  subshelf: discovery
  tags: ab, test, analysis, product
  added: "2026-11-25"
  featured: false
  source: import
  author: Pawel Huryn
  authorUrl: "https://github.com/phuryn"
  authorKind: person
  curator: Brandon
  upstream: phuryn/pm-skills
  upstreamCommit: 9af7bfd0bc47fdad43c2eaa7a43cd13918e7aaef
  upstreamPath: pm-data-analytics/skills/ab-test-analysis/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2026 Pawel Huryn
---

# Ab test analysis

Do this one job: an A/B readout. Adapted from `phuryn/pm-skills` at commit `9af7bfd0bc47` (MIT). Copyright (c) 2026 Pawel Huryn

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Restate the hypothesis, the variant, the primary metric, any guardrail metric, the traffic split, and the dates. Use a dash when a field is missing.
3. Compute a rate and a relative lift only from counts the user supplied. If either arm is missing, leave the lift unknown. Do not invent a sample size, a p-value, or a confidence interval.
4. If the user supplied a significance result, quote it. If they did not, say significance is unknown. Do not treat a positive trend as a win.
5. Note a guardrail the user said moved the wrong way. A primary lift with a broken guardrail is not a ship.
6. Recommend one of ship, extend, or stop, and name the missing fact that would change the call. Show the readout and wait.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Control 1000 visitors, 40 conversions. Variant 1000 visitors, 52 conversions. Primary metric is signup. No guardrail was tracked. The test ran four days. I do not have a p-value.

Agent: Lift is (52-40)/40 = 30% from the counts given. Significance stays unknown. Recommendation is extend, because four days and no significance result cannot support a ship.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
