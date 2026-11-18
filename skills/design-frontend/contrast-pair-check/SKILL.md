---
name: contrast-pair-check
description: >-
  Computes the WCAG 2 contrast ratio of two opaque sRGB colors the user
  supplies. Use when the user asks whether a foreground and background pair
  meets a contrast threshold they name.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/contrast_pair.py. No network and no browser.
metadata:
  category: design-frontend
  subshelf: accessibility
  tags: contrast, wcag, color
  added: "2026-11-18"
  featured: false
---

# Contrast pair check

Report the contrast ratio of two colors the user typed. Use [scripts/contrast_pair.py](scripts/contrast_pair.py). The formula and the figures they might name are in [references/wcag-contrast.md](references/wcag-contrast.md). Do not sample a screenshot, and do not claim the screen conforms.

## Steps

1. Take the foreground and the background as opaque hex (`#RGB` or `#RRGGBB`). If either color is missing, stop and ask. Do not assume white, and do not convert a translucent color.
2. If they named a threshold, keep their number. If they named a WCAG figure in words ("normal text", "large text", "non-text", "enhanced"), use 4.5, 3, 3, or 7 from the reference, and say which one. If they named no threshold, pass none.
3. Run `python3 scripts/contrast_pair.py` with `--foreground`, `--background`, and `--threshold` only when they named one. The same command covers a terminal ink on paper, a landing-page button, or a chat bubble. Do not compute the ratio by hand.
4. Check that the printed foreground and background match the hex they typed, and that `threshold` is their number or empty. `meets=true` means the rounded ratio is at least that number. `meets=not-applied` means no number was compared.
5. State that the result is this pair only. A border, a font size, and the rest of the screen were not measured.

## Example

User: On the order ticket, the bid label is `#9A9286` on paper `#14120E`. Does that pair meet 4.5?

Agent: Runs `python3 scripts/contrast_pair.py --foreground 9A9286 --background 14120E --threshold 4.5`.

```
foreground=#9A9286
background=#14120E
lighter=#9A9286
darker=#14120E
ratio=6.0839
threshold=4.5
meets=true
```

The 4.5 figure is the one they asked about. Large text and non-text were not applied. This is not a conformance claim, and no price was read.

## Boundaries

Do not open a browser, pick a brand color, or round a miss up to a pass. If the script cannot run, say so instead of inventing a ratio.
