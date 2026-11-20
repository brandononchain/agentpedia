#!/usr/bin/env python3
"""Report the last USER in each Dockerfile stage and the last HEALTHCHECK.

Instruction behavior follows the Dockerfile reference: FROM starts a stage,
USER applies to the rest of that stage, and only the last HEALTHCHECK takes
effect. The best-practices page is why a user token of root is labeled root.
https://docs.docker.com/reference/dockerfile/
https://docs.docker.com/build/building/best-practices/

The script reads one local file. It does not build an image or pull a base.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SIZE_LIMIT = 1_000_000
INSTRUCTIONS = {
    "from",
    "run",
    "cmd",
    "label",
    "maintainer",
    "expose",
    "env",
    "add",
    "copy",
    "entrypoint",
    "volume",
    "user",
    "workdir",
    "arg",
    "onbuild",
    "stopsignal",
    "healthcheck",
    "shell",
}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(2)


def strip_inline(line: str) -> str:
    stripped = line.lstrip()
    if stripped.startswith("#"):
        return ""
    mark = stripped.find(" #")
    if mark != -1:
        stripped = stripped[:mark]
    return stripped.rstrip()


def directive_end(raw_lines: list[str]) -> tuple[int, str]:
    escape = "\\"
    consumed = 0
    while consumed < len(raw_lines):
        stripped = raw_lines[consumed].strip()
        if stripped == "" or not stripped.startswith("#"):
            break
        body = stripped[1:].strip()
        if "=" not in body:
            break
        key, value = body.split("=", 1)
        key = key.strip().lower()
        value = value.strip()
        if key == "escape":
            if value not in {"\\", "`"}:
                fail("escape directive must be \\ or backtick")
            escape = value
            consumed += 1
            continue
        if key in {"syntax", "check"}:
            consumed += 1
            continue
        break
    return consumed, escape


def logical_lines(text: str) -> list[tuple[int, str]]:
    if len(text.encode("utf-8")) > SIZE_LIMIT:
        fail(f"file is over {SIZE_LIMIT} bytes")
    if text.startswith("\ufeff"):
        text = text.lstrip("\ufeff")
    raw_lines = text.splitlines()
    consumed, escape = directive_end(raw_lines)
    logical: list[tuple[int, str]] = []
    start: int | None = None
    parts: list[str] = []
    for number, line in enumerate(raw_lines, start=1):
        if number <= consumed:
            continue
        continued = line.endswith(escape) and not line.endswith(escape * 2)
        chunk = line[:-1].rstrip() if continued else line
        if start is None:
            start = number
            parts = [chunk]
        else:
            parts.append(chunk.lstrip())
        if continued:
            continue
        joined = parts[0]
        for extra in parts[1:]:
            joined += "" if joined.endswith(" ") else " "
            joined += extra
        logical.append((start, joined))
        start = None
        parts = []
    if start is not None:
        fail(f"line {start} continues past the end of the file")
    return logical


def parse_from(rest: str, number: int) -> tuple[str, str, str]:
    tokens = rest.split()
    if not tokens:
        fail(f"FROM on line {number} has no image")
    platform = "absent"
    index = 0
    while index < len(tokens) and tokens[index].startswith("--"):
        token = tokens[index]
        if not token.startswith("--platform="):
            fail(f"FROM on line {number} has a flag other than --platform=")
        platform = token.split("=", 1)[1]
        if platform == "":
            fail(f"FROM on line {number} has an empty --platform")
        index += 1
    if index >= len(tokens):
        fail(f"FROM on line {number} has no image")
    image = tokens[index]
    index += 1
    name = "absent"
    if index < len(tokens):
        if tokens[index].lower() != "as" or index + 1 >= len(tokens):
            fail(f"FROM on line {number} is not an image or AS name")
        name = tokens[index + 1]
        index += 2
        if index != len(tokens):
            fail(f"FROM on line {number} has extra text")
    return image, name, platform


def parse_health(rest: str, number: int) -> str:
    tokens = rest.split()
    if not tokens:
        fail(f"HEALTHCHECK on line {number} has no form")
    if tokens[0].lower() == "none":
        if len(tokens) != 1:
            fail(f"HEALTHCHECK on line {number} is not NONE or CMD")
        return "none"
    lowered = [token.lower() for token in tokens]
    if "cmd" not in lowered:
        fail(f"HEALTHCHECK on line {number} is not NONE or CMD")
    cmd_at = lowered.index("cmd")
    if cmd_at == len(tokens) - 1:
        fail(f"HEALTHCHECK on line {number} has no command")
    for token in tokens[:cmd_at]:
        if not token.startswith("--"):
            fail(f"HEALTHCHECK on line {number} is not NONE or CMD")
    return "cmd"


def blank_stage(number: int, image: str, name: str, platform: str) -> dict[str, str]:
    return {
        "from_line": str(number),
        "image": image,
        "name": name,
        "platform": platform,
        "user": "unset",
        "user_line": "absent",
        "user_count": "0",
        "user_root": "no",
        "user_numeric": "no",
    }


def parse_text(text: str) -> dict:
    stages: list[dict[str, str]] = []
    health = {"form": "absent", "count": "0", "line": "absent"}
    health_count = 0
    for number, raw in logical_lines(text):
        body = strip_inline(raw)
        if not body:
            continue
        if "<<" in body:
            fail(f"heredoc on line {number} is not read")
        word, _, rest = body.partition(" ")
        instruction = word.lower()
        if instruction not in INSTRUCTIONS:
            fail(f"unparsed line {number}")
        if instruction == "from":
            image, name, platform = parse_from(rest.strip(), number)
            stages.append(blank_stage(number, image, name, platform))
            continue
        if not stages and instruction != "arg":
            fail(f"line {number} is before FROM")
        if instruction == "user":
            tokens = rest.split()
            if len(tokens) != 1:
                fail(f"USER on line {number} is not one user token")
            user = tokens[0]
            user_part = user.split(":", 1)[0]
            stage = stages[-1]
            stage["user"] = user
            stage["user_line"] = str(number)
            stage["user_count"] = str(int(stage["user_count"]) + 1)
            stage["user_root"] = "yes" if user_part == "root" else "no"
            stage["user_numeric"] = "yes" if user_part.isdigit() else "no"
        elif instruction == "healthcheck":
            health_count += 1
            health = {
                "form": parse_health(rest.strip(), number),
                "count": str(health_count),
                "line": str(number),
            }
    if not stages:
        fail("no FROM instruction")
    return {"stages": stages, "health": health}


def format_report(parsed: dict) -> str:
    rows = ["ok=yes", f"stages={len(parsed['stages'])}"]
    for index, stage in enumerate(parsed["stages"]):
        rows.extend(
            [
                f"stage={index}",
                f"from_line={stage['from_line']}",
                f"image={stage['image']}",
                f"name={stage['name']}",
                f"platform={stage['platform']}",
                f"user={stage['user']}",
                f"user_line={stage['user_line']}",
                f"user_count={stage['user_count']}",
                f"user_root={stage['user_root']}",
                f"user_numeric={stage['user_numeric']}",
            ]
        )
    health = parsed["health"]
    rows.extend(
        [
            f"healthcheck={health['form']}",
            f"healthcheck_count={health['count']}",
            f"healthcheck_line={health['line']}",
        ]
    )
    return "\n".join(rows)


def report_text(text: str) -> str:
    return format_report(parse_text(text))


def expect_exit(text: str, message: str) -> None:
    try:
        report_text(text)
    except SystemExit as exc:
        if exc.code != 2:
            fail(f"self-test {message} exited with the wrong status")
        return
    fail(f"self-test accepted {message}")


def self_test() -> None:
    fixture = (Path(__file__).resolve().parents[1] / "assets" / "Dockerfile").read_text(encoding="utf-8")
    report = report_text(fixture)
    for line in (
        "ok=yes",
        "stages=2",
        "stage=0",
        "image=ubuntu:24.04",
        "name=base",
        "user=unset",
        "user_root=no",
        "stage=1",
        "image=base",
        "name=absent",
        "user=app",
        "user_count=1",
        "user_root=no",
        "healthcheck=cmd",
        "healthcheck_count=1",
    ):
        if line not in report.splitlines():
            fail(f"self-test missing {line}")

    none = report_text("FROM alpine\nHEALTHCHECK CMD true\nHEALTHCHECK NONE\n")
    if "healthcheck=none" not in none or "healthcheck_count=2" not in none:
        fail("self-test did not keep the last HEALTHCHECK")

    root = report_text("FROM alpine\nUSER root\nUSER app:app\n")
    if "user=app:app" not in root or "user_count=2" not in root or "user_root=yes" in root:
        fail("self-test kept an earlier root user")

    numeric = report_text("FROM alpine\nUSER 0\n")
    if "user=0" not in numeric or "user_numeric=yes" not in numeric or "user_root=yes" in numeric:
        fail("self-test called UID 0 root")

    named_root = report_text("FROM alpine\nUSER root:root\n")
    if "user_root=yes" not in named_root:
        fail("self-test missed USER root")

    platform = report_text("FROM --platform=linux/amd64 ubuntu AS app\n")
    if "platform=linux/amd64" not in platform or "name=app" not in platform:
        fail("self-test missed --platform or AS")

    escaped = report_text("# escape=`\nFROM alpine\nHEALTHCHECK --interval=5m `\n  CMD true\n")
    if "healthcheck=cmd" not in escaped:
        fail("self-test missed a backtick continuation")

    expect_exit("USER app\nFROM alpine\n", "USER before FROM")
    expect_exit("FROM alpine\nRUN <<EOF\necho hi\nEOF\n", "a heredoc")
    expect_exit("# comment only\n", "a file with no FROM")
    expect_exit("FROM --reset=user alpine\n", "FROM --reset")
    print("self-test=ok")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dockerfile", nargs="?", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.dockerfile is None:
        fail("pass a Dockerfile, or --self-test")
    if not args.dockerfile.is_file():
        fail(f"file not found: {args.dockerfile}")
    text = args.dockerfile.read_text(encoding="utf-8")
    sys.stdout.write(report_text(text) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
