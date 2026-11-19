#!/usr/bin/env python3
"""Check one message against Conventional Commits 1.0.0.

The rules are the specification at
https://www.conventionalcommits.org/en/v1.0.0/#specification
This script does not apply a 50-character subject limit, and it does not
decide the next version number.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HEADER_RE = re.compile(
    r"^(?P<type>[A-Za-z0-9]+)"
    r"(?:\((?P<scope>[^()\s]+)\))?"
    r"(?P<bang>!)?"
    r": (?P<description>\S.*)$"
)
TOKEN_RE = re.compile(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*")


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(2)


def split_footer(line: str) -> tuple[str, str, bool] | None:
    if line.startswith("BREAKING CHANGE: "):
        return "BREAKING CHANGE", line[len("BREAKING CHANGE: ") :], True
    if line.startswith("BREAKING-CHANGE: "):
        return "BREAKING-CHANGE", line[len("BREAKING-CHANGE: ") :], True
    match = TOKEN_RE.match(line)
    if not match:
        return None
    rest = line[match.end() :]
    if rest.startswith(": "):
        return match.group(0), rest[2:], False
    if rest.startswith(" #"):
        return match.group(0), rest[2:], False
    return None


def parse_footer_paragraph(lines: list[str]) -> list[tuple[str, str, bool]] | None:
    if not lines:
        return None
    first = split_footer(lines[0])
    if first is None:
        return None
    footers: list[tuple[str, str, bool]] = []
    token, value, breaking = first
    for line in lines[1:]:
        nxt = split_footer(line)
        if nxt is None:
            value = value + "\n" + line
            continue
        footers.append((token, value.strip(), breaking))
        token, value, breaking = nxt
    footers.append((token, value.strip(), breaking))
    return footers


def body_and_footers(lines: list[str]) -> tuple[list[tuple[str, str, bool]]]:
    while lines and lines[-1].strip() == "":
        lines.pop()
    if not lines:
        return []
    start = 0
    for index, line in enumerate(lines):
        if line.strip() == "":
            start = index + 1
    parsed = parse_footer_paragraph(lines[start:])
    if parsed is None:
        return []
    return parsed


def parse_message(text: str) -> dict[str, object]:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if normalized.strip() == "":
        return {"ok": False, "reason": "empty"}
    lines = normalized.splitlines()
    header = HEADER_RE.fullmatch(lines[0])
    if header is None:
        return {"ok": False, "reason": "header"}
    if len(lines) > 1 and lines[1].strip() != "":
        return {"ok": False, "reason": "blank-line"}
    footers = body_and_footers(lines[2:])
    footer_breaking = any(item[2] for item in footers)
    prefix_breaking = header.group("bang") == "!"
    if prefix_breaking and footer_breaking:
        breaking_from = "both"
    elif prefix_breaking:
        breaking_from = "prefix"
    elif footer_breaking:
        breaking_from = "footer"
    else:
        breaking_from = "none"
    return {
        "ok": True,
        "type": header.group("type"),
        "scope": header.group("scope") or "",
        "breaking": prefix_breaking or footer_breaking,
        "breaking_from": breaking_from,
        "footers": [(item[0], item[1]) for item in footers],
    }


def render(result: dict[str, object]) -> list[str]:
    if not result["ok"]:
        return ["ok=no", f"reason={result['reason']}"]
    lines = [
        "ok=yes",
        f"type={result['type']}",
        f"scope={result['scope']}",
        f"breaking={'yes' if result['breaking'] else 'no'}",
        f"breaking_from={result['breaking_from']}",
        f"footers={len(result['footers'])}",
    ]
    for token, _value in result["footers"]:
        lines.append(f"footer_token={token}")
    return lines


def self_test() -> None:
    both = parse_message(
        "feat!: drop support for Node 6\n"
        "\n"
        "BREAKING CHANGE: use JavaScript features not available in Node 6.\n"
    )
    expect(
        both,
        ok=True,
        type="feat",
        scope="",
        breaking=True,
        breaking_from="both",
        tokens=["BREAKING CHANGE"],
    )
    prefix = parse_message("feat(api)!: send an email to the customer when a product is shipped\n")
    expect(prefix, ok=True, type="feat", scope="api", breaking=True, breaking_from="prefix", tokens=[])
    docs = parse_message("docs: correct spelling of CHANGELOG\n")
    expect(docs, ok=True, type="docs", scope="", breaking=False, breaking_from="none", tokens=[])
    lang = parse_message("feat(lang): add Polish language\n")
    expect(lang, ok=True, type="feat", scope="lang", breaking=False, breaking_from="none", tokens=[])
    cased = parse_message("Feat(Parser): Add arrays\n")
    expect(cased, ok=True, type="Feat", scope="Parser", breaking=False, breaking_from="none", tokens=[])
    synonym = parse_message("fix: remove the flag\n\nBREAKING-CHANGE: the flag is gone\n")
    expect(
        synonym,
        ok=True,
        type="fix",
        scope="",
        breaking=True,
        breaking_from="footer",
        tokens=["BREAKING-CHANGE"],
    )
    trailers = parse_message(
        "fix: prevent racing of requests\n"
        "\n"
        "Introduce a request id and a reference to latest request. Dismiss\n"
        "incoming responses other than from latest request.\n"
        "\n"
        "Remove timeouts which were used to mitigate the racing issue but are\n"
        "obsolete now.\n"
        "\n"
        "Reviewed-by: Z\n"
        "Refs: #123\n"
    )
    expect(
        trailers,
        ok=True,
        type="fix",
        scope="",
        breaking=False,
        breaking_from="none",
        tokens=["Reviewed-by", "Refs"],
    )
    hash_sep = parse_message("chore: note the review\n\nRefs #123\n")
    expect(hash_sep, ok=True, type="chore", scope="", breaking=False, breaking_from="none", tokens=["Refs"])
    buried = parse_message(
        "feat: add flag\n\nBREAKING CHANGE: not a footer yet\n\nbecause another paragraph follows\n"
    )
    expect(buried, ok=True, type="feat", scope="", breaking=False, breaking_from="none", tokens=[])
    stuck = parse_message("feat: add flag\n\nBody text.\nReviewed-by: Z\n")
    expect(stuck, ok=True, type="feat", scope="", breaking=False, breaking_from="none", tokens=[])
    for text in ("fix:no space\n", "feat(): empty scope\n", "feat: \n", "not a commit\n"):
        bad = parse_message(text)
        if bad["ok"]:
            fail(f"self-test accepted {text!r}")
        if bad["reason"] != "header":
            fail(f"self-test header reason for {text!r} was {bad['reason']}")
    blank = parse_message("feat: add arrays\nForgot the blank line.\n")
    if blank["ok"] or blank["reason"] != "blank-line":
        fail(f"self-test blank-line: {blank}")
    empty = parse_message(" \n")
    if empty["ok"] or empty["reason"] != "empty":
        fail(f"self-test empty: {empty}")
    print("self-test=ok")


def expect(result: dict[str, object], **wanted: object) -> None:
    tokens = [item[0] for item in result.get("footers", [])]
    actual = {
        "ok": result["ok"],
        "type": result.get("type"),
        "scope": result.get("scope"),
        "breaking": result.get("breaking"),
        "breaking_from": result.get("breaking_from"),
        "tokens": tokens,
    }
    for key, value in wanted.items():
        if actual[key] != value:
            fail(f"self-test {key}={actual[key]!r} expected {value!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("message", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if args.message is None:
        fail("pass a message file, or --self-test")
    if not args.message.is_file():
        fail(f"not a file: {args.message}")
    text = args.message.read_text(encoding="utf-8")
    print("\n".join(render(parse_message(text))))


if __name__ == "__main__":
    main()
