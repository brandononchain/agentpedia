# What the scan reports

`scripts/scan_overflow.py` reads one stylesheet and one viewport width in CSS pixels. Each finding is one declaration. `findings=` is the count. Zero means none of these patterns were in the file. It does not mean a browser will skip the horizontal scrollbar.

Kinds:

- `px-wider-than-viewport`. `width`, `min-width`, or `flex-basis` is a plain `px` length greater than the viewport.
- `viewport-unit`. A length on width, min-width, max-width, flex-basis, left, right, inset, margin, or padding uses `vw`, `dvw`, `svw`, or `lvw` at 100 or more. The classic `vw` unit includes the scrollbar, so `100vw` can be wider than the page the person sees.
- `negative-margin`. `margin-left`, `margin-right`, or the horizontal side of the `margin` shorthand is negative.
- `max-content`. `width`, `min-width`, or `flex-basis` is `max-content` or `min-content`. Those sizes do not shrink to the viewport. The text was not measured.
- `nowrap`. `white-space` is `nowrap` or `pre`. That is a risk only when the content is wider than the viewport. The content was not measured.

`applies=yes` means there is no media query, or the query is a simple `min-width` / `max-width` in `px` that this viewport matches, including a `screen and (...)` form. `applies=unresolved` means the query used a feature the script does not evaluate, so the finding might not apply. A query the viewport cannot match is left out.

`same_rule_overflow` is `clip`, `hidden`, `auto`, `scroll`, `visible`, or `absent`, taken from that same rule. Clipping the element does not prove the parent stays inside the viewport.

The script does not resolve custom properties, `rem`, `em`, or a `calc()` that is not already a plain `px` or a viewport unit above. It does not read Tailwind class names in HTML. It skips keyframes and font faces. A nested selector is joined with a space, or by replacing `&`. Comma groups in a parent selector are not rewritten. A slash in `media` separates a query nested inside another.

This is not a browser layout.
