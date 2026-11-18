# Contrast ratio

The number `scripts/contrast_pair.py` prints is the WCAG 2 contrast ratio of two opaque sRGB colors. [WCAG 2.2](https://www.w3.org/TR/WCAG22/#dfn-contrast-ratio) defines that ratio as the lighter relative luminance plus 0.05, divided by the darker relative luminance plus 0.05. Relative luminance uses the sRGB weights 0.2126, 0.7152, and 0.0722, and the 0.04045 cutoff in the [relative luminance definition](https://www.w3.org/TR/WCAG22/#dfn-relative-luminance). This script uses 0.04045, not the older 0.03928 cutoff.

The printed ratio is rounded half up to four decimal places. `meets` compares that rounded ratio with the threshold the user passed. With no threshold, `meets` is `not-applied`.

Figures a user may name, which the script does not choose:

- 4.5, the WCAG 2.2 minimum for normal text (success criterion 1.4.3).
- 3, the large-text figure in that criterion, and the non-text figure for a user-interface component or a meaningful graphic (1.4.11).
- 7, the enhanced figure for normal text (1.4.6).

Large text in that guideline is about 18pt, or 14pt bold. The script never sees the font, so it cannot decide that a pair is large. A missing color stops the run. White is not filled in. `#777777` on `#FFFFFF` is 4.4781, which misses 4.5. The self-test locks that pair.

One pair is not a conformance claim for a screen.
