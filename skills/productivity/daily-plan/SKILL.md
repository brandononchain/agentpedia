---
name: daily-plan
description: >-
  Picks three outcomes for a workday and a not-today list from a longer task
  dump. Use when the user asks to plan the day or to cut a task list down.
license: Apache-2.0
metadata:
  category: productivity
  tags: planning
  added: "2026-11-05"
  featured: false
---

# Daily plan

Reduce a task dump to three outcomes that can finish today, plus an explicit not-today list. Do not sneak the whole list back in as "small tasks."

## Steps

1. Read the tasks and any fixed commitments (meetings, deadlines today). Ask for the stop time if it matters and was not given.
2. Choose three outcomes. An outcome is a finished thing, not a topic ("send the review notes", not "look at PRs").
3. Put everything else on not-today, including tasks that feel urgent but do not fit.
4. Note which outcome is first, based on a real deadline or a dependency the user named. If none, pick the one the user said matters most, or ask.
5. Validate the plan: three outcomes, each completable in the day they described, and no fourth hiding in a bullet. Show the plan.

## Example

User: Tasks are write the Skilldex README, review a 40-file PR, book travel, and answer 30 emails. They have two hours.

Agent: Outcomes — finish the README draft, and send a review limited to blockers on the PR. Not today — travel booking and the inbox, with a note that two hours cannot hold all four. First is the README, because the user listed it first and no deadline was attached to the others. The inbox is not added back as a third outcome.

## Boundaries

Do not schedule the user's personal life in detail they did not ask to plan. Do not turn the plan into a minute-by-minute script.
