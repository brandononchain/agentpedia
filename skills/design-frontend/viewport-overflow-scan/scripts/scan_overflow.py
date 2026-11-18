#!/usr/bin/env python3
"""Flag CSS declarations that can force horizontal overflow at one viewport.

This is not a layout engine. It does not resolve custom properties, it does
not measure text, and it does not claim the page scrolls.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from decimal import Decimal


WIDTH_PROPS = {"width", "min-width", "flex-basis"}
VIEWPORT_PROPS = WIDTH_PROPS | {
    "max-width",
    "left",
    "right",
    "margin",
    "margin-left",
    "margin-right",
    "padding",
    "padding-left",
    "padding-right",
    "inset",
    "inset-inline",
    "inset-inline-start",
    "inset-inline-end",
}
SKIP_AT = {
    "keyframes",
    "-webkit-keyframes",
    "-moz-keyframes",
    "font-face",
    "page",
    "counter-style",
    "property",
}
VW_RE = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(vw|dvw|svw|lvw)\b", re.I)
PX_RE = re.compile(r"^(-?(?:\d+\.?\d*|\.\d+))px$", re.I)


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def one_line(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def strip_comments(text: str) -> str:
    out: list[str] = []
    index = 0
    while index < len(text):
        if text.startswith("/*", index):
            end = text.find("*/", index + 2)
            if end == -1:
                break
            index = end + 2
            continue
        out.append(text[index])
        index += 1
    return "".join(out)


class Parser:
    def __init__(self, css: str) -> None:
        self.css = css
        self.n = len(css)
        self.i = 0

    def peek(self) -> str:
        return self.css[self.i] if self.i < self.n else ""

    def skip_ws(self) -> None:
        while self.i < self.n and self.css[self.i].isspace():
            self.i += 1

    def skip_string(self) -> None:
        quote = self.css[self.i]
        self.i += 1
        while self.i < self.n:
            char = self.css[self.i]
            if char == "\\":
                self.i += 2
                continue
            self.i += 1
            if char == quote:
                return

    def read_until(self) -> str:
        start = self.i
        while self.i < self.n:
            char = self.css[self.i]
            if char in "\"'":
                self.skip_string()
                continue
            if char in "{;":
                return self.css[start : self.i]
            self.i += 1
        return self.css[start : self.i]

    def read_block(self) -> str:
        if self.peek() != "{":
            return ""
        self.i += 1
        start = self.i
        depth = 1
        while self.i < self.n and depth:
            char = self.css[self.i]
            if char in "\"'":
                self.skip_string()
                continue
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    body = self.css[start : self.i]
                    self.i += 1
                    return body
            self.i += 1
        return self.css[start : self.i]


def split_commas(text: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")" and depth:
            depth -= 1
        elif char == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
            continue
        buf.append(char)
    if buf:
        parts.append("".join(buf))
    return parts


def branch_applies(branch: str, viewport: Decimal) -> bool | None:
    text = branch.strip()
    if re.search(r"\bnot\b", text, re.I):
        return None
    for part in re.split(r"\s+and\s+", text, flags=re.I):
        part = part.strip()
        part = re.sub(r"^(only\s+)?(all|screen|print|speech)\b\s*", "", part, flags=re.I).strip()
        if not part:
            continue
        match = re.fullmatch(
            r"\(?\s*(min-width|max-width)\s*:\s*([0-9]*\.?[0-9]+)px\s*\)?",
            part,
            flags=re.I,
        )
        if not match:
            return None
        limit = Decimal(match.group(2))
        if match.group(1).lower() == "min-width" and viewport < limit:
            return False
        if match.group(1).lower() == "max-width" and viewport > limit:
            return False
    return True


def media_applies(query: str, viewport: Decimal) -> bool | None:
    text = query.strip()
    if not text:
        return True
    results = [branch_applies(branch, viewport) for branch in split_commas(text)]
    if any(result is True for result in results):
        return True
    if results and all(result is False for result in results):
        return False
    return None


def plain_px(value: str) -> Decimal | None:
    match = PX_RE.fullmatch(value.strip())
    if not match:
        return None
    return Decimal(match.group(1))


def split_tokens(value: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    quote = ""
    index = 0
    while index < len(value):
        char = value[index]
        if quote:
            buf.append(char)
            if char == "\\" and index + 1 < len(value):
                buf.append(value[index + 1])
                index += 2
                continue
            if char == quote:
                quote = ""
            index += 1
            continue
        if char in "\"'":
            quote = char
            buf.append(char)
        elif char == "(":
            depth += 1
            buf.append(char)
        elif char == ")" and depth:
            depth -= 1
            buf.append(char)
        elif char.isspace() and depth == 0:
            if buf:
                parts.append("".join(buf))
                buf = []
        else:
            buf.append(char)
        index += 1
    if buf:
        parts.append("".join(buf))
    return parts


def negative_token(token: str) -> bool:
    return bool(re.match(r"^-\d", token))


def horizontal_negative(value: str) -> bool:
    parts = split_tokens(value)
    if not parts or len(parts) > 4:
        return False
    if len(parts) == 4:
        return negative_token(parts[1]) or negative_token(parts[3])
    horizontal = parts[0] if len(parts) == 1 else parts[1]
    return negative_token(horizontal)


def clean_value(value: str) -> str:
    text = one_line(value)
    return re.sub(r"\s*!important\s*$", "", text, flags=re.I).strip()


def combine_selector(parent: str, nested: str) -> str:
    nested = one_line(nested)
    if "&" in nested:
        return one_line(nested.replace("&", parent))
    return one_line(f"{parent} {nested}")


def overflow_of(decls: list[tuple[str, str]]) -> str:
    raw = ""
    for prop, value in decls:
        if prop == "overflow":
            parts = value.lower().split()
            if parts:
                raw = parts[0]
    for prop, value in decls:
        if prop == "overflow-x":
            parts = value.lower().split()
            if parts:
                raw = parts[0]
    if raw in {"hidden", "clip", "auto", "scroll", "visible"}:
        return raw
    return "absent"


def finding(
    kind: str,
    selector: str,
    prop: str,
    value: str,
    media: str,
    applies: str,
    viewport: Decimal,
    same: str,
    extra: dict[str, str] | None = None,
) -> dict[str, str]:
    item = {
        "kind": kind,
        "selector": selector or "(no selector)",
        "property": prop,
        "value": value,
        "media": media or "none",
        "applies": applies,
        "viewport": format(viewport, "f"),
        "same_rule_overflow": same,
    }
    if extra:
        item.update(extra)
    return item


def from_decls(
    selector: str,
    decls: list[tuple[str, str]],
    media: str,
    applies: str,
    viewport: Decimal,
) -> list[dict[str, str]]:
    same = overflow_of(decls)
    found: list[dict[str, str]] = []
    for prop, value in decls:
        if prop in WIDTH_PROPS:
            px = plain_px(value)
            if px is not None and px > viewport:
                found.append(
                    finding(
                        "px-wider-than-viewport",
                        selector,
                        prop,
                        value,
                        media,
                        applies,
                        viewport,
                        same,
                        {"px": format(px, "f")},
                    )
                )
            elif value.lower() in {"max-content", "min-content"}:
                found.append(
                    finding("max-content", selector, prop, value, media, applies, viewport, same)
                )
        if prop in VIEWPORT_PROPS:
            for match in VW_RE.finditer(value):
                number = Decimal(match.group(1))
                if number >= 100:
                    unit = f"{format(number, 'f')}{match.group(2).lower()}"
                    found.append(
                        finding(
                            "viewport-unit",
                            selector,
                            prop,
                            value,
                            media,
                            applies,
                            viewport,
                            same,
                            {"unit": unit},
                        )
                    )
        if prop in {"margin-left", "margin-right"} and (
            (plain_px(value) is not None and plain_px(value) < 0) or negative_token(value)
        ):
            found.append(finding("negative-margin", selector, prop, value, media, applies, viewport, same))
        elif prop == "margin" and horizontal_negative(value):
            found.append(finding("negative-margin", selector, prop, value, media, applies, viewport, same))
        if prop == "white-space" and value.lower() in {"nowrap", "pre"}:
            found.append(finding("nowrap", selector, prop, value, media, applies, viewport, same))
    return found


def parse_style(
    body: str,
    selector: str,
    media: str,
    applies: str,
    viewport: Decimal,
) -> list[dict[str, str]]:
    parser = Parser(body)
    decls: list[tuple[str, str]] = []
    found: list[dict[str, str]] = []
    while parser.i < parser.n:
        parser.skip_ws()
        if parser.i >= parser.n or parser.peek() == "}":
            break
        chunk = parser.read_until()
        if parser.peek() == ";":
            parser.i += 1
            if ":" in chunk:
                prop, value = chunk.split(":", 1)
                prop = prop.strip().lower()
                if prop:
                    decls.append((prop, clean_value(value)))
            continue
        if parser.peek() != "{":
            break
        nested_body = parser.read_block()
        header = chunk.strip()
        if header.startswith("@"):
            name = header.split(None, 1)[0].lower().lstrip("@")
            if name == "media":
                query = one_line(re.sub(r"^@media\s+", "", header, flags=re.I))
                state = media_applies(query, viewport)
                if state is False:
                    continue
                child_media = query if media == "none" else f"{media} / {query}"
                child_applies = "unresolved" if state is None or applies == "unresolved" else "yes"
                found.extend(parse_style(nested_body, selector, child_media, child_applies, viewport))
            continue
        found.extend(
            parse_style(nested_body, combine_selector(selector, header), media, applies, viewport)
        )
    found.extend(from_decls(selector, decls, media, applies, viewport))
    return found


def parse_sheet(css: str, media: str, applies: str, viewport: Decimal) -> list[dict[str, str]]:
    parser = Parser(css)
    found: list[dict[str, str]] = []
    while parser.i < parser.n:
        parser.skip_ws()
        if parser.i >= parser.n or parser.peek() == "}":
            break
        chunk = parser.read_until()
        if parser.peek() == ";":
            parser.i += 1
            continue
        if parser.peek() != "{":
            break
        body = parser.read_block()
        header = chunk.strip()
        if header.startswith("@"):
            name = header.split(None, 1)[0].lower().lstrip("@")
            if name in SKIP_AT:
                continue
            if name == "media":
                query = one_line(re.sub(r"^@media\s+", "", header, flags=re.I))
                state = media_applies(query, viewport)
                if state is False:
                    continue
                child_media = query if media == "none" else f"{media} / {query}"
                child_applies = "unresolved" if state is None or applies == "unresolved" else "yes"
                found.extend(parse_sheet(body, child_media, child_applies, viewport))
                continue
            if name == "supports":
                found.extend(parse_sheet(body, media, applies, viewport))
                continue
            child_media = one_line(header) if name == "container" else media
            child_applies = "unresolved" if name == "container" else applies
            found.extend(parse_sheet(body, child_media, child_applies, viewport))
            continue
        found.extend(parse_style(body, one_line(header), media, applies, viewport))
    return found


def scan_css(css: str, viewport: Decimal) -> list[dict[str, str]]:
    return parse_sheet(strip_comments(css), "none", "yes", viewport)


def format_px(token: str) -> str:
    return format(Decimal(token).normalize(), "f")


def render(item: dict[str, str]) -> str:
    parts = [
        f"kind={item['kind']}",
        f"selector={json.dumps(item['selector'], ensure_ascii=True)}",
        f"property={item['property']}",
        f"value={json.dumps(item['value'], ensure_ascii=True)}",
        f"media={json.dumps(item['media'], ensure_ascii=True)}",
        f"applies={item['applies']}",
        f"viewport={format_px(item['viewport'])}",
        f"same_rule_overflow={item['same_rule_overflow']}",
    ]
    if "px" in item:
        parts.append(f"px={format_px(item['px'])}")
    if "unit" in item:
        parts.append(f"unit={item['unit']}")
    return " ".join(parts)


FIXTURE = """
/* min-width: 9999px and 100vw in a comment are not declarations */
.blotter { min-width: 720px; }
.blotter th { white-space: nowrap; }
.ticket { width: 100vw; }
.bleed { margin: 0 -16px; }
.clip { min-width: 800px; overflow-x: clip; }
.ok { width: 100%; max-width: 40rem; }
.icon { width: 16px; }
.row { min-width: max-content; }
@media (min-width: 800px) {
  .desk { min-width: 960px; }
}
@media (max-width: 400px) {
  .phone { min-width: 480px; }
}
@media (min-width: 100px) and (orientation: portrait) {
  .maybe { width: 100dvw; }
}
@keyframes slide {
  from { min-width: 2000px; }
}
.card {
  width: 20px;
  .title { white-space: pre; }
}
"""


def self_test() -> None:
    found = scan_css(FIXTURE, Decimal("390"))
    keys = [(item["kind"], item["selector"], item["property"]) for item in found]
    expected = [
        ("px-wider-than-viewport", ".blotter", "min-width"),
        ("nowrap", ".blotter th", "white-space"),
        ("viewport-unit", ".ticket", "width"),
        ("negative-margin", ".bleed", "margin"),
        ("px-wider-than-viewport", ".clip", "min-width"),
        ("max-content", ".row", "min-width"),
        ("px-wider-than-viewport", ".phone", "min-width"),
        ("viewport-unit", ".maybe", "width"),
        ("nowrap", ".card .title", "white-space"),
    ]
    if keys != expected:
        fail("self-test findings:\n" + "\n".join(render(item) for item in found))
    clip = next(item for item in found if item["selector"] == ".clip")
    if clip["same_rule_overflow"] != "clip":
        fail("self-test missed overflow-x on .clip")
    maybe = next(item for item in found if item["selector"] == ".maybe")
    if maybe["applies"] != "unresolved" or maybe["unit"] != "100dvw":
        fail("self-test misread the unresolved media query")
    phone = next(item for item in found if item["selector"] == ".phone")
    if phone["applies"] != "yes" or phone["media"] != "(max-width: 400px)":
        fail("self-test dropped a max-width query that still matches")
    if any(item["selector"] == ".desk" for item in found):
        fail("self-test kept a min-width query the viewport misses")
    if any("2000" in item["value"] for item in found):
        fail("self-test read a keyframe")
    print("self-test=ok")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--css", help="Path to a CSS file")
    parser.add_argument("--viewport", help="Viewport width in CSS pixels")
    parser.add_argument("--self-test", action="store_true", help="Check a built-in stylesheet and exit")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.css or not args.viewport:
        fail("pass --css and --viewport, or --self-test")
    try:
        viewport = Decimal(args.viewport)
    except Exception:
        fail("viewport must be a number of CSS pixels")
    if not viewport.is_finite() or viewport <= 0:
        fail("viewport must be a positive number of CSS pixels")
    try:
        css = open(args.css, encoding="utf-8").read()
    except OSError as exc:
        fail(f"could not read {args.css}: {exc}")
    found = scan_css(css, viewport)
    for item in found:
        print(render(item))
    print(f"findings={len(found)}")
    print(f"viewport={format(viewport.normalize(), 'f')}")


if __name__ == "__main__":
    main()
