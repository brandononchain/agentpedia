#!/usr/bin/env python3
"""Pick the highest SemVer bump from classified commit types.

fix is patch, feat is minor, and a breaking commit is major, including when
the type is neither fix nor feat. Other types do not bump. That correlation
is the Conventional Commits FAQ:
https://www.conventionalcommits.org/en/v1.0.0/#how-does-this-relate-to-semver
The numbers themselves follow Semantic Versioning 2.0.0:
https://semver.org/#summary
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TYPE_RE = re.compile(r"^[A-Za-z0-9]+$")
# The numbered expression published at https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
)
class PlanError(Exception):
    pass


def fail(message: str) -> None:
    raise PlanError(message)


def classify(type_name: str, breaking: bool) -> str:
    if breaking:
        return "major"
    folded = type_name.casefold()
    if folded == "feat":
        return "minor"
    if folded == "fix":
        return "patch"
    return "none"


def parse_lines(text: str) -> list[tuple[int, str, bool, str]]:
    rows: list[tuple[int, str, bool, str]] = []
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if line == "" or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) == 1:
            type_name, breaking = parts[0], False
        elif len(parts) == 2 and parts[1] == "breaking":
            type_name, breaking = parts[0], True
        else:
            fail(f"line {number}: expected '<type>' or '<type> breaking'")
        if not TYPE_RE.fullmatch(type_name):
            fail(f"line {number}: type is not one word of letters and digits")
        rows.append((number, type_name, breaking, classify(type_name, breaking)))
    if not rows:
        fail("no classified commits")
    return rows


def parse_current(value: str) -> tuple[re.Match[str], bool]:
    if value.startswith("v") or value.startswith("V"):
        fail(f"{value} starts with v, which is not a semantic version")
    match = SEMVER_RE.fullmatch(value)
    if match is None:
        fail(f"not a semantic version: {value}")
    return match, match.group(5) is not None


def next_version(match: re.Match[str], bump: str) -> tuple[str, str, str]:
    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3))
    prerelease = "yes" if match.group(4) is not None else "no"
    initial = "yes" if major == 0 else "no"
    if prerelease == "yes" or initial == "yes" or bump == "none":
        nxt = "unchanged" if bump == "none" and prerelease == "no" and initial == "no" else "not-computed"
        if bump == "none" and (prerelease == "yes" or initial == "yes"):
            nxt = "not-computed"
        return prerelease, initial, nxt
    if bump == "major":
        nxt = f"{major + 1}.0.0"
    elif bump == "minor":
        nxt = f"{major}.{minor + 1}.0"
    else:
        nxt = f"{major}.{minor}.{patch + 1}"
    return prerelease, initial, nxt


def render(rows: list[tuple[int, str, bool, str]], current: str | None) -> list[str]:
    counts = {"major": 0, "minor": 0, "patch": 0, "none": 0}
    lines: list[str] = []
    for number, type_name, breaking, kind in rows:
        counts[kind] += 1
        lines.append(
            f"line={number} type={type_name} breaking={'yes' if breaking else 'no'} class={kind}"
        )
    bump = "none"
    for name in ("patch", "minor", "major"):
        if counts[name]:
            bump = name
    lines.extend(
        [
            f"commits={len(rows)}",
            f"major={counts['major']}",
            f"minor={counts['minor']}",
            f"patch={counts['patch']}",
            f"none={counts['none']}",
            f"bump={bump}",
        ]
    )
    if current is None:
        return lines
    match, has_build = parse_current(current)
    prerelease, initial, nxt = next_version(match, bump)
    lines.append(f"current={current}")
    if has_build:
        lines.append("build=ignored")
    lines.extend(
        [
            f"prerelease={prerelease}",
            f"initial_development={initial}",
            f"next={nxt}",
        ]
    )
    return lines


def self_test() -> None:
    text = "feat\nfix\n# comment\n\ndocs\nchore breaking\n"
    lines = render(parse_lines(text), "1.4.2")
    expect(
        lines,
        [
            "line=1 type=feat breaking=no class=minor",
            "line=2 type=fix breaking=no class=patch",
            "line=5 type=docs breaking=no class=none",
            "line=6 type=chore breaking=yes class=major",
            "commits=4",
            "major=1",
            "minor=1",
            "patch=1",
            "none=1",
            "bump=major",
            "current=1.4.2",
            "prerelease=no",
            "initial_development=no",
            "next=2.0.0",
        ],
    )
    feat_break = render(parse_lines("Feat breaking\n"), "1.4.2")
    if "class=major" not in feat_break[0] or "next=2.0.0" not in feat_break:
        fail("self-test feat breaking did not outrank minor: " + " | ".join(feat_break))
    none = render(parse_lines("docs\nchore\n"), "1.4.2")
    if "bump=none" not in none or "next=unchanged" not in none:
        fail("self-test none: " + " | ".join(none))
    patch = render(parse_lines("fix\n"), "2.0.1")
    if "next=2.0.2" not in patch:
        fail("self-test patch: " + " | ".join(patch))
    minor = render(parse_lines("feat\nfix\n"), "3.1.4")
    if "next=3.2.0" not in minor or "bump=minor" not in minor:
        fail("self-test minor: " + " | ".join(minor))
    zero = render(parse_lines("feat\n"), "0.3.1")
    if "initial_development=yes" not in zero or "next=not-computed" not in zero:
        fail("self-test zero: " + " | ".join(zero))
    pre = render(parse_lines("fix\n"), "1.2.3-alpha")
    if "prerelease=yes" not in pre or "next=not-computed" not in pre:
        fail("self-test prerelease: " + " | ".join(pre))
    built = render(parse_lines("fix\n"), "1.2.3+sha")
    if "build=ignored" not in built or "next=1.2.4" not in built:
        fail("self-test build: " + " | ".join(built))
    for bad in ("v1.2.3", "01.2.3", "1.2", "1.2.3-"):
        try:
            parse_current(bad)
        except PlanError:
            continue
        fail(f"self-test accepted version {bad}")
    try:
        parse_lines("feat extra\n")
    except PlanError:
        pass
    else:
        fail("self-test accepted an extra token")
    try:
        parse_lines("# only a comment\n")
    except PlanError:
        pass
    else:
        fail("self-test accepted an empty classification")
    print("self-test=ok")


def expect(lines: list[str], wanted: list[str]) -> None:
    if lines != wanted:
        fail("self-test lines:\n" + "\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--types", type=Path)
    parser.add_argument("--current", default="")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    try:
        if args.self_test:
            self_test()
            return
        if args.types is None:
            fail("pass --types, or --self-test")
        if not args.types.is_file():
            fail(f"not a file: {args.types}")
        current = args.current.strip() or None
        rows = parse_lines(args.types.read_text(encoding="utf-8"))
        report = render(rows, current)
    except PlanError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from exc
    print("\n".join(report))


if __name__ == "__main__":
    main()
