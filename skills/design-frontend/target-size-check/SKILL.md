---
name: target-size-check
description: >-
  Compares a control width and height in CSS pixels with a minimum target size
  the user names. Use when the user asks whether a button, link, or other target
  meets a size they specify.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/check_target.py. No browser and no network.
metadata:
  category: design-frontend
  subshelf: accessibility
  tags: target-size, wcag, css
  added: "2026-11-18"
  featured: false
---

# Target size check

Compare one control's box with a minimum the user names. Use [scripts/check_target.py](scripts/check_target.py). The two published CSS-pixel figures, and the exceptions the script ignores, are in [references/wcag-target-size.md](references/wcag-target-size.md).

## Steps

1. Take width and height in CSS pixels from the user. A missing or non-positive side stops the run. Do not measure a screenshot.
2. Take the minimum they named. If they say "WCAG 2.2 target size minimum", the published figure is 24. If they say "enhanced", it is 44. If they name neither a number nor one of those two, ask. Do not pick 24 or 44 for them.
3. Run `python3 scripts/check_target.py` with `--width`, `--height`, and `--minimum`. The same command fits a send control, a close-position control, or a signup button.
4. Check that the printed width, height, and minimum match what they gave. `meets=true` only when both sides are at least the minimum. Report each `short_by` as printed.
5. If they already described an exception from the reference, write that sentence beside the result and do not change `meets`. If they did not, write "exception not described". Do not call the screen conformant.

## Example

User: The send control on the assistant composer is 20 by 20 CSS pixels. Check it against 24.

Agent: Runs `python3 scripts/check_target.py --width 20 --height 20 --minimum 24`.

```
width=20
height=20
minimum=24
width_short_by=4
height_short_by=4
meets=false
```

Exception not described, so none is applied. This is the one control, not a conformance claim.

## Boundaries

Do not grow the control, invent a tap-target padding, or place the control on a page. Spacing between neighbors was not measured.
