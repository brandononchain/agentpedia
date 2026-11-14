---
name: ui-review-notes
description: >-
  Writes review notes for a screen the user describes, tied to the states they
  named. Use when the user asks for a UI review of a page, a component, or a
  screenshot description before it is built or merged.
license: Apache-2.0
metadata:
  category: design-frontend
  subshelf: review
  tags: ui, review
  added: "2026-11-10"
  featured: false
---

# UI review notes

Review the screen in front of you. Notes name a state and a problem a person can check. Do not redesign the product.

## Steps

1. List the states the user described: empty, loading, ready, error, and any others they named. A state they did not describe is "not shown".
2. For each shown state, write at most three notes. Each note says what is on the screen and what is unclear or missing.
3. Separate visual notes from behavior notes. A missing label is visual. A button that does not say what it submits is behavior.
4. Check that every note points at something they described. Delete a note that depends on a screenshot you do not have.
5. End with the single change you would ask for first, and say the rest can wait. Do not invent a new feature.

## Example

User: The billing page shows a total and a Pay button. There is no empty state, and the error state is a red banner that says "failed".

Agent: Ready is shown: a total and Pay. Empty is not shown. Error is shown, and the banner does not say what failed or what to do next. First change: name the failure in the banner. The review does not add a new plan or a new price.

## Boundaries

Do not claim a measurement from a picture you were not given. Do not rewrite the visual system.
