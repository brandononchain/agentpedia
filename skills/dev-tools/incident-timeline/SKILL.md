---
name: incident-timeline
description: >-
  Builds a timestamped incident timeline from logs, alerts, and notes the user
  supplies. Use when the user asks to reconstruct an outage, write a timeline,
  or start a postmortem.
license: Apache-2.0
metadata:
  category: dev-tools
  subshelf: incidents
  tags: incidents
  added: "2026-11-08"
  featured: false
---

# Incident timeline

Reconstruct what happened from the evidence the user pastes. Keep times, sources, and uncertainty visible. Do not fill gaps with a plausible story.

## Steps

1. Collect every timestamped event from the notes, alerts, and log lines provided. Normalize them to one timezone and say which one.
2. Sort them. If two events conflict, keep both and mark the conflict.
3. Write the timeline as time, source, and fact. Separate customer impact from internal signals.
4. Add a short "unknown" list for questions the evidence does not answer: trigger, duration, and who was affected.
5. Validate every line by pointing back at a supplied event. Delete any line that is an inference, or move it to a clearly labeled inference section.

## Example

User: Build a timeline. 14:02 page from the error budget alert. 14:11 deploy of `billing-232`. 14:19 error rate back under the budget. Timezone is UTC.

Agent: 14:02 UTC — alert — error budget page fired. 14:11 UTC — deploy note — `billing-232` shipped. 14:19 UTC — alert — error rate back under budget. Unknown: whether the deploy caused the errors, and which customers saw failures. No inference recorded as fact.

## Boundaries

Do not name a root cause the evidence does not show. Do not include customer data that was not required to explain the impact.
