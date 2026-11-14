---
name: home-week-plan
description: >-
  Lays out a week of home admin and appointments from tasks and fixed times the
  user lists. Use when the user asks to schedule errands, chores, or a household
  calendar without dropping a commitment they already have.
license: Apache-2.0
metadata:
  category: personal-life
  subshelf: home
  tags: scheduling, home
  added: "2026-11-10"
  featured: false
---

# Home week plan

Place tasks around commitments. Do not drop a fixed appointment to make the week look calmer.

## Steps

1. List fixed commitments first, with the day and time they gave. Those blocks are not movable.
2. List the tasks they want done, and any deadline they named. A task with no deadline is "this week" only if they said the horizon is this week.
3. Place tasks in the open time they described. If they did not describe open time, return a list grouped by deadline and do not invent hours.
4. Check that every fixed commitment is still on the plan at the original time, and that every task appears once.
5. If the tasks do not fit the time they described, say what does not fit. Do not silently cut a task.

## Example

User: Tuesday 09:00 dentist, fixed. Tasks: pay the water bill (due Wednesday) and replace the entry bulb (no deadline). They said evenings are open. Horizon is this week.

Agent: Tuesday 09:00 dentist stays. The water bill is placed before Wednesday. The bulb is placed on an evening and marked as having no deadline. Nothing is removed. No hour is invented for the bulb beyond "an evening".

## Boundaries

Do not cancel an appointment, and do not add a chore they did not ask for.
