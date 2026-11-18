#!/usr/bin/env python3
"""Compare a control's CSS width and height with a minimum the caller names.

Both sides must be at least the minimum. The script does not apply spacing,
inline, equivalent-control, user-agent, or essential exceptions.
"""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal, ROUND_HALF_UP


class SizeError(ValueError):
    pass


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def parse_px(token: str, label: str) -> Decimal:
    try:
        value = Decimal(token)
    except Exception as exc:
        raise SizeError(f"{label} must be a number of CSS pixels") from exc
    if not value.is_finite() or value <= 0:
        raise SizeError(f"{label} must be a positive number of CSS pixels")
    return value


def show(value: Decimal) -> str:
    shown = value.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    text = f"{shown:.4f}".rstrip("0").rstrip(".")
    return text or "0"


def report(width: Decimal, height: Decimal, minimum: Decimal) -> list[str]:
    width_short = minimum - width if width < minimum else Decimal(0)
    height_short = minimum - height if height < minimum else Decimal(0)
    meets = width >= minimum and height >= minimum
    return [
        f"width={show(width)}",
        f"height={show(height)}",
        f"minimum={show(minimum)}",
        f"width_short_by={show(width_short)}",
        f"height_short_by={show(height_short)}",
        f"meets={'true' if meets else 'false'}",
    ]


def self_test() -> None:
    cases = [
        ("20", "20", "24", "4", "4", "false"),
        ("48", "32", "24", "0", "0", "true"),
        ("44", "44", "44", "0", "0", "true"),
        ("23.5", "24", "24", "0.5", "0", "false"),
    ]
    for width, height, minimum, width_short, height_short, meets in cases:
        parsed = dict(
            item.split("=", 1)
            for item in report(parse_px(width, "width"), parse_px(height, "height"), parse_px(minimum, "minimum"))
        )
        expected = {
            "width_short_by": width_short,
            "height_short_by": height_short,
            "meets": meets,
        }
        for key, value in expected.items():
            if parsed[key] != value:
                fail(f"self-test {width}x{height} min {minimum}: {key}={parsed[key]} expected {value}")
    try:
        parse_px("0", "width")
    except SizeError:
        pass
    else:
        fail("self-test accepted a zero size")
    print("self-test=ok")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--width", help="Control width in CSS pixels")
    parser.add_argument("--height", help="Control height in CSS pixels")
    parser.add_argument("--minimum", help="Minimum CSS pixels required on both sides")
    parser.add_argument("--self-test", action="store_true", help="Check known sizes and exit")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.width or not args.height or not args.minimum:
        fail("pass --width, --height, and --minimum, or --self-test")
    try:
        width = parse_px(args.width, "width")
        height = parse_px(args.height, "height")
        minimum = parse_px(args.minimum, "minimum")
    except SizeError as exc:
        fail(str(exc))
    print("\n".join(report(width, height, minimum)))


if __name__ == "__main__":
    main()
