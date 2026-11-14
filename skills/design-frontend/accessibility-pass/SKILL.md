---
name: accessibility-pass
description: >-
  Checks a component the user describes against the four WCAG principles and
  records what was not shown. Use when the user asks for an accessibility pass
  on a screen, a form, or a widget.
license: Apache-2.0
metadata:
  category: design-frontend
  subshelf: accessibility
  tags: accessibility, ui
  added: "2026-11-10"
  featured: false
---

# Accessibility pass

Write what a keyboard user and a screen-reader user would be missing, from the description the user gave. Use the principle names in [references/principles.md](references/principles.md).

## Steps

1. List the controls they named. A control with no name is an operable and understandable gap.
2. For each principle, write shown or not shown, with one sentence. Do not mark a principle passed because the others look fine.
3. If they give two colors, you may say whether the pair is the paper and ink of a design system they named. Do not compute a contrast ratio unless they also give the ratio or ask you to calculate it from hex values they typed.
4. Check every gap against their description. If they did not mention focus order, write "focus order not described" rather than a guess.
5. End with the first gap to fix. Do not claim WCAG conformance.

## Example

User: A div that looks like a button says "Continue". It has no role. The error is red text on a white field, and I do not have a contrast number.

Agent: Operable: the control is not named as a button, so a keyboard user may not reach it. Perceivable: color is used, and no contrast ratio was supplied, so contrast is not shown. Understandable: "Continue" does not say what continues. First gap: make it a button with a specific name. This is not a conformance claim.

## Boundaries

Do not certify the screen. Do not invent alt text for an image you were not shown.
