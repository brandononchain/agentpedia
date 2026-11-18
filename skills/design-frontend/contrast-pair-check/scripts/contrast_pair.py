#!/usr/bin/env python3
"""Contrast ratio of two opaque sRGB colors, using the WCAG 2 formula.

The ratio is rounded half up to four decimal places. A threshold is applied
only when the caller passes one. Translucent colors are rejected.
"""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal, ROUND_HALF_UP


class ColorError(ValueError):
    pass


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def parse_hex(token: str) -> tuple[int, int, int]:
    text = token.strip()
    if text.startswith("#"):
        text = text[1:]
    if len(text) in {4, 8}:
        raise ColorError("translucent hex is not accepted; composite onto a background and pass the opaque color")
    if len(text) == 3:
        text = "".join(ch * 2 for ch in text)
    if len(text) != 6 or any(ch not in "0123456789abcdefABCDEF" for ch in text):
        raise ColorError(f"not an opaque sRGB hex color: {token}")
    return int(text[0:2], 16), int(text[2:4], 16), int(text[4:6], 16)


def channel(byte: int) -> float:
    srgb = byte / 255.0
    if srgb <= 0.04045:
        return srgb / 12.92
    return ((srgb + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    red, green, blue = rgb
    return 0.2126 * channel(red) + 0.7152 * channel(green) + 0.0722 * channel(blue)


def contrast_ratio(foreground: tuple[int, int, int], background: tuple[int, int, int]) -> tuple[Decimal, tuple[int, int, int], tuple[int, int, int]]:
    fore = relative_luminance(foreground)
    back = relative_luminance(background)
    if fore >= back:
        lighter, darker = foreground, background
        light_l, dark_l = fore, back
    else:
        lighter, darker = background, foreground
        light_l, dark_l = back, fore
    raw = (light_l + 0.05) / (dark_l + 0.05)
    shown = Decimal(str(raw)).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)
    return shown, lighter, darker


def fmt_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def lines(foreground: str, background: str, threshold: str | None) -> list[str]:
    try:
        fore = parse_hex(foreground)
        back = parse_hex(background)
    except ColorError as exc:
        fail(str(exc))
    shown, lighter, darker = contrast_ratio(fore, back)
    if threshold is None:
        meets = "not-applied"
        threshold_text = ""
    else:
        try:
            limit = Decimal(threshold)
        except Exception:
            fail("threshold must be a number")
        if not limit.is_finite() or limit <= 0:
            fail("threshold must be a positive number")
        meets = "true" if shown >= limit else "false"
        threshold_text = threshold.strip()
    return [
        f"foreground={fmt_hex(fore)}",
        f"background={fmt_hex(back)}",
        f"lighter={fmt_hex(lighter)}",
        f"darker={fmt_hex(darker)}",
        f"ratio={shown:.4f}",
        f"threshold={threshold_text}",
        f"meets={meets}",
    ]


def self_test() -> None:
    cases = [
        ("#000000", "#FFFFFF", None, "21.0000", "not-applied", "#FFFFFF", "#000000"),
        ("#FFFFFF", "#FFFFFF", None, "1.0000", "not-applied", "#FFFFFF", "#FFFFFF"),
        ("#777", "#fff", "4.5", "4.4781", "false", "#FFFFFF", "#777777"),
        ("#767676", "#FFFFFF", "4.5", "4.5422", "true", "#FFFFFF", "#767676"),
        ("#9A9286", "#14120E", "4.5", "6.0839", "true", "#9A9286", "#14120E"),
        ("#9A9286", "#14120E", "7", "6.0839", "false", "#9A9286", "#14120E"),
    ]
    for foreground, background, threshold, ratio, meets, lighter, darker in cases:
        got = lines(foreground, background, threshold)
        expected = {
            "ratio": ratio,
            "meets": meets,
            "lighter": lighter,
            "darker": darker,
        }
        parsed = dict(item.split("=", 1) for item in got)
        for key, value in expected.items():
            if parsed[key] != value:
                fail(f"self-test {foreground} on {background}: {key}={parsed[key]} expected {value}")
    try:
        parse_hex("#77777780")
    except ColorError as exc:
        if "translucent" not in str(exc):
            fail(f"self-test rejected alpha for the wrong reason: {exc}")
    else:
        fail("self-test accepted a translucent color")
    print("self-test=ok")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--foreground", help="Opaque sRGB hex, #RGB or #RRGGBB")
    parser.add_argument("--background", help="Opaque sRGB hex, #RGB or #RRGGBB")
    parser.add_argument("--threshold", help="Compare the rounded ratio with this number")
    parser.add_argument("--self-test", action="store_true", help="Check known pairs and exit")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.foreground or not args.background:
        fail("pass --foreground and --background, or --self-test")
    print("\n".join(lines(args.foreground, args.background, args.threshold)))


if __name__ == "__main__":
    main()
