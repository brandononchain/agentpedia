#!/usr/bin/env python3
"""Classify each uses: value in a GitHub Actions workflow file.

The forms come from the workflow syntax for steps and reusable workflows,
and from the secure-use guidance on full-length commit SHAs.
https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
https://docs.github.com/en/actions/reference/security/secure-use

The script reads one local file. It does not fetch a commit, and it does not
look for a dependency lockfile.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SIZE_LIMIT = 1_000_000
KEY_RE = re.compile(r"[A-Za-z0-9_-]+")
SHA_RE = re.compile(r"[0-9a-fA-F]{40}")
BLOCK_RE = re.compile(r"[|>][+-]?\d*")


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(2)


def strip_comment(raw: str) -> str:
    out: list[str] = []
    quote = ""
    index = 0
    while index < len(raw):
        char = raw[index]
        if quote:
            out.append(char)
            if char == quote and not (quote == '"' and index > 0 and raw[index - 1] == "\\"):
                quote = ""
            index += 1
            continue
        if char in {'"', "'"}:
            quote = char
            out.append(char)
            index += 1
            continue
        if char == "#":
            break
        out.append(char)
        index += 1
    return "".join(out).rstrip()


def indent_of(raw: str, line_no: int) -> int:
    index = 0
    while index < len(raw) and raw[index] == " ":
        index += 1
    if index < len(raw) and raw[index] == "\t":
        fail(f"tab-indent on line {line_no}")
    return index


def split_key(text: str) -> tuple[str, str, bool] | None:
    if ":" not in text:
        return None
    key, rest = text.split(":", 1)
    if not KEY_RE.fullmatch(key):
        return None
    value = rest.strip()
    return key, value, value != ""


def is_block_value(value: str) -> bool:
    return BLOCK_RE.fullmatch(value) is not None


def unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


class Line:
    def __init__(self, number: int, indent: int, text: str) -> None:
        self.number = number
        self.indent = indent
        self.text = text


class Frame:
    def __init__(self, indent: int, role: str, name: str | None = None) -> None:
        self.indent = indent
        self.role = role
        self.name = name


def logical_lines(text: str) -> list[Line]:
    if len(text.encode("utf-8")) > SIZE_LIMIT:
        fail(f"file is over {SIZE_LIMIT} bytes")
    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff")
    lines: list[Line] = []
    block_at: int | None = None
    for number, raw in enumerate(text.splitlines(), start=1):
        if raw.strip() == "":
            continue
        indent = indent_of(raw, number)
        content = strip_comment(raw).strip()
        if content == "":
            continue
        if content in {"---", "..."}:
            fail(f"document marker on line {number} is not read")
        if block_at is not None:
            if indent > block_at:
                continue
            block_at = None
        if opens_block(content):
            block_at = indent
        lines.append(Line(number, indent, content))
    return lines


def opens_block(text: str) -> bool:
    body = text[1:].strip() if text.startswith("-") else text
    split = split_key(body)
    if split is None:
        return False
    _key, value, has = split
    return has and is_block_value(value)


def classify_value(value: str) -> tuple[str, str, str, str]:
    suffix = "no"
    prefix = "no"
    ref = "absent"
    if value.startswith("docker://"):
        kind = "docker"
    elif value.startswith("$/"):
        kind = "self-repo"
        if "@" in value[2:]:
            suffix = "invalid"
            ref = value.split("@", 1)[1]
    elif value.startswith("./"):
        kind = "relative"
        if "@" in value[2:]:
            suffix = "invalid"
            ref = value.split("@", 1)[1]
    elif "${{" in value:
        kind = "expression"
    elif "@" in value:
        ref = value.rsplit("@", 1)[1]
        kind = "sha" if SHA_RE.fullmatch(ref) else "movable"
    else:
        kind = "missing-ref"
    if ref.startswith("refs/"):
        prefix = "yes"
    return kind, ref, suffix, prefix


def parse_lines(lines: list[Line]) -> list[dict[str, str]]:
    stack = [Frame(-1, "root")]
    found: list[dict[str, str]] = []

    def job_name() -> str:
        for frame in reversed(stack):
            if frame.role == "job":
                return frame.name or "absent"
        return "absent"

    def where() -> str:
        roles = {frame.role for frame in stack}
        if "step" in roles:
            return "step"
        if "job" in roles:
            return "job"
        return "other"

    def handle_pair(text: str, indent: int, number: int) -> None:
        split = split_key(text)
        if split is None:
            fail(f"unparsed line {number}")
        key, value, has = split
        parent = stack[-1]
        if key == "uses":
            if not has or is_block_value(value):
                fail(f"uses on line {number} has no one-line value")
            shown = unquote(value)
            if shown == "":
                fail(f"uses on line {number} has extra text")
            if any(char.isspace() for char in shown) and "${{" not in shown:
                fail(f"uses on line {number} has extra text")
            kind, ref, suffix, prefix = classify_value(shown)
            found.append(
                {
                    "line": str(number),
                    "where": where(),
                    "job": job_name(),
                    "value": shown,
                    "kind": kind,
                    "ref": ref,
                    "suffix": suffix,
                    "prefix": prefix,
                }
            )
            return
        if parent.role == "root" and key == "jobs":
            if has:
                fail(f"jobs on line {number} is not a block")
            stack.append(Frame(indent, "jobs"))
            return
        if parent.role == "jobs":
            if has:
                fail(f"job {key} on line {number} is not a block")
            stack.append(Frame(indent, "job", key))
            return
        if parent.role == "job" and key == "steps":
            if has:
                fail(f"steps on line {number} is not a block")
            stack.append(Frame(indent, "steps"))
            return
        if not has:
            stack.append(Frame(indent, "map"))

    for line in lines:
        while stack[-1].indent >= line.indent:
            stack.pop()
        if line.text.startswith("-"):
            body = line.text[1:].strip()
            parent = stack[-1]
            if parent.role == "steps":
                stack.append(Frame(line.indent, "step"))
                if body:
                    handle_pair(body, line.indent, line.number)
            elif body and split_key(body) is not None:
                stack.append(Frame(line.indent, "item"))
                handle_pair(body, line.indent, line.number)
            elif body and ":" in body:
                fail(f"unparsed line {line.number}")
            continue
        handle_pair(line.text, line.indent, line.number)
    return found


def format_report(found: list[dict[str, str]]) -> str:
    counts = {
        "sha": 0,
        "movable": 0,
        "self-repo": 0,
        "relative": 0,
        "docker": 0,
        "missing-ref": 0,
        "expression": 0,
    }
    suffix_invalid = 0
    rows = ["ok=yes"]
    for item in found:
        counts[item["kind"]] += 1
        if item["suffix"] == "invalid":
            suffix_invalid += 1
        rows.extend(
            [
                f"line={item['line']}",
                f"where={item['where']}",
                f"job={item['job']}",
                f"value={item['value']}",
                f"kind={item['kind']}",
                f"ref={item['ref']}",
                f"suffix={item['suffix']}",
                f"prefix={item['prefix']}",
            ]
        )
    rows.extend(
        [
            f"uses={len(found)}",
            f"sha={counts['sha']}",
            f"movable={counts['movable']}",
            f"self_repo={counts['self-repo']}",
            f"relative={counts['relative']}",
            f"docker={counts['docker']}",
            f"missing_ref={counts['missing-ref']}",
            f"expression={counts['expression']}",
            f"suffix_invalid={suffix_invalid}",
        ]
    )
    return "\n".join(rows)


def report_text(text: str) -> str:
    return format_report(parse_lines(logical_lines(text)))


def self_test() -> None:
    fixture = (Path(__file__).resolve().parents[1] / "assets" / "workflow.yml").read_text(encoding="utf-8")
    report = report_text(fixture)
    expected = [
        "kind=sha",
        "value=actions/checkout@8f4b7f84864484a7bf31766abe9204da3cbe65b3",
        "kind=movable",
        "value=actions/setup-node@v6",
        "kind=relative",
        "value=./.github/actions/hello-world-action",
        "kind=self-repo",
        "value=$/.github/actions/hello-world-action",
        "kind=docker",
        "value=docker://alpine:3.8",
        "where=job",
        "kind=sha",
        "value=octo-org/this-repo/.github/workflows/workflow-1.yml@172239021f7ba04fe7327647b213799853a9eb89",
        "uses=6",
        "sha=2",
        "movable=1",
        "self_repo=1",
        "relative=1",
        "docker=1",
        "missing_ref=0",
        "expression=0",
        "suffix_invalid=0",
    ]
    for line in expected:
        if line not in report.splitlines():
            fail(f"self-test missing {line}")

    hidden = report_text(
        "jobs:\n  test:\n    steps:\n      - run: |\n          echo uses: actions/checkout@v1\n"
        "      - uses: actions/checkout@v6\n"
    )
    if "actions/checkout@v1" in hidden or "\nuses=1\n" not in f"\n{hidden}\n":
        fail("self-test counted a uses value inside a block scalar")

    short = report_text("jobs:\n  test:\n    steps:\n      - uses: actions/checkout@abc1234\n")
    if "kind=sha" in short or "kind=movable" not in short:
        fail("self-test treated a short ref as a full SHA")

    missing = report_text("jobs:\n  test:\n    steps:\n      - uses: actions/checkout\n")
    if "kind=missing-ref" not in missing:
        fail("self-test missed a uses value with no ref")

    suffixed = report_text("jobs:\n  test:\n    steps:\n      - uses: $/actions/mine@v1\n")
    if "suffix=invalid" not in suffixed or "kind=self-repo" not in suffixed:
        fail("self-test missed an invalid self-repo suffix")

    prefixed = report_text(
        "jobs:\n  call:\n    uses: octo-org/repo/.github/workflows/ci.yml@refs/heads/main\n"
    )
    if "prefix=yes" not in prefixed or "where=job" not in prefixed:
        fail("self-test missed a refs/ prefix")

    expressed = report_text("jobs:\n  test:\n    steps:\n      - uses: ${{ github.repository }}@v1\n")
    if "kind=expression" not in expressed or "kind=sha" in expressed:
        fail("self-test classified an expression as a ref")

    commented = report_text("jobs:\n  test:\n    steps:\n      - uses: actions/checkout@v6 # later\n")
    if "value=actions/checkout@v6" not in commented or "later" in commented:
        fail("self-test kept a comment on a uses line")

    digest = report_text(
        "jobs:\n  test:\n    steps:\n      - uses: docker://alpine@sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb\n"
    )
    if "kind=docker" not in digest or "kind=sha" in digest:
        fail("self-test treated a docker image as a git SHA")

    try:
        report_text("jobs:\n\ttest:\n")
    except SystemExit as exc:
        if exc.code != 2:
            fail("self-test tab-indent exited with the wrong status")
    else:
        fail("self-test accepted a tab indent")
    print("self-test=ok")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workflow", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.workflow is None:
        fail("pass a workflow file, or --self-test")
    if not args.workflow.is_file():
        fail(f"file not found: {args.workflow}")
    text = args.workflow.read_text(encoding="utf-8")
    sys.stdout.write(report_text(text) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
