# Target size

WCAG 2.2 publishes two pointer-target sizes. [Target Size (Minimum)](https://www.w3.org/TR/WCAG22/#target-size-minimum) is 24 by 24 CSS pixels. [Target Size (Enhanced)](https://www.w3.org/TR/WCAG22/#target-size-enhanced) is 44 by 44 CSS pixels. Pass `--minimum 24` or `--minimum 44` only when the user named that figure.

`scripts/check_target.py` returns `meets=true` only when both the width and the height are at least that minimum. The same size counts as meeting it. The shortfall on each side is `minimum` minus the side, or 0 when the side is already large enough.

The script does not apply the exceptions in those criteria:

- spacing, including the 24 CSS pixel circles in the minimum criterion
- a different control on the same page that already meets the size
- a target inside a sentence, or one whose size is the line height
- a control whose size comes from the user agent
- a size the user calls essential

If the user already described one of those, write it down and leave `meets` as the script printed it. Do not invent an exception to flip the result.

One control is not a conformance claim.
