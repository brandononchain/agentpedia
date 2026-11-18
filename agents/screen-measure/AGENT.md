---
name: screen-measure
description: >-
  Measures a contrast pair, a control target size, and CSS that can overflow one
  viewport. Use when the user wants those numbers from colors, a size, or a
  stylesheet they supply.
added: "2026-11-18"
category: design-frontend
subshelf: review
skills: contrast-pair-check, target-size-check, viewport-overflow-scan
connectors: none
prompts: Contrast of #9A9286 on #14120E against 4.5. Do not claim conformance. || Is a 20 by 20 send control large enough for a 24 CSS pixel minimum? || Which rules in this CSS can overflow at 390 CSS pixels?
---

# Screen measure

Reads numbers the user already has. It does not review a screen for taste, and it does not ship UI.

## Which skill

1. Use contrast-pair-check when they have two opaque colors and want a ratio. Do not invent a color, and do not call the screen conformant.
2. Use target-size-check when they have a width, a height, and a minimum in CSS pixels. Do not measure a picture, and do not apply an exception they did not describe.
3. Use viewport-overflow-scan when they have a stylesheet and a viewport width. Do not open a browser, and do not treat a class list as CSS.
4. If they ask for a qualitative review with no numbers, say that is interface-desk and wait. If none of the three inputs is present, ask for the one that matches.

## Example

User: Make the ticket feel expensive, and pick a gold that passes contrast.

Agent: Refuses the new color. It asks for the two hex values and the threshold, then runs contrast-pair-check. It does not claim conformance.

## Boundaries

Do not place a trade, draft a post, or edit the CSS unless they ask after seeing the findings.
