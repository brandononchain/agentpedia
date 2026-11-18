---
name: viewport-overflow-scan
description: >-
  Flags CSS declarations that can force horizontal overflow at a viewport width
  the user names. Use when the user asks why a layout might scroll sideways on
  a narrow screen.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/scan_overflow.py. Reads a local CSS file. No
  browser and no network.
metadata:
  category: design-frontend
  subshelf: review
  tags: overflow, css, viewport
  added: "2026-11-18"
  featured: false
---

# Viewport overflow scan

List declarations in a stylesheet that can force horizontal overflow at one viewport width. Use [scripts/scan_overflow.py](scripts/scan_overflow.py). What each kind means, and what is not measured, is in [references/overflow-kinds.md](references/overflow-kinds.md).

## Steps

1. Take a CSS file the user points at and a viewport width in CSS pixels. If either is missing, ask. Do not assume 390, and do not open a browser.
2. Run `python3 scripts/scan_overflow.py` with `--css` and `--viewport`. The same scan fits a blotter, a pricing row, or a thread of posts. Class names in HTML are not CSS; say so and stop if that is all they have.
3. Keep every printed finding. A query the viewport cannot match is already omitted. For `applies=unresolved`, say the finding might not apply at this width.
4. Check each finding against the file: the `value` has to appear on that property. Drop a line that does not. `nowrap` and `max-content` are risks until the user supplies content that is wider than the viewport. Do not invent that content.
5. End with the count the script printed. Say this is not a layout, so it does not prove the page scrolls or that it does not.

## Example

User: Here is `blotter.css`. What can force sideways scroll at 390 CSS pixels?

```css
.blotter { min-width: 720px; }
.blotter th { white-space: nowrap; }
.ticket { width: 100vw; }
@media (min-width: 800px) {
  .desk { min-width: 960px; }
}
```

Agent: Runs `python3 scripts/scan_overflow.py --css blotter.css --viewport 390`.

```
kind=px-wider-than-viewport selector=".blotter" property=min-width value="720px" media="none" applies=yes viewport=390 same_rule_overflow=absent px=720
kind=nowrap selector=".blotter th" property=white-space value="nowrap" media="none" applies=yes viewport=390 same_rule_overflow=absent
kind=viewport-unit selector=".ticket" property=width value="100vw" media="none" applies=yes viewport=390 same_rule_overflow=absent unit=100vw
findings=3
viewport=390
```

The blotter min-width is 720, wider than 390. The header cells do not wrap, and the header text was not in the file. `100vw` is a viewport unit of 100. The 960px rule sits in a min-width of 800, so it is not in the list. No column and no price were added. This does not prove the browser scrolls.

## Boundaries

Do not edit the CSS unless they ask. Do not treat a Tailwind class list as a stylesheet. Do not claim a scrollbar from a finding alone.
