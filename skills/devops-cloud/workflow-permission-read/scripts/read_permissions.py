#!/usr/bin/env python3
"""Read permissions keys in one GitHub Actions workflow file.

Scope names and access levels are the set in the workflow syntax example
for GITHUB_TOKEN permissions.
https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax

The script reads one local file. It does not call GitHub, and it does not
know the enterprise, organization, or repository default.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SIZE_LIMIT = 1_000_000
KEY_RE = re.compile(r"[A-Za-z0-9_-]+")
BLOCK_RE = re.compile(r"[|>][+-]?\d*")
EVENT_RE = re.compile(r"(?<![A-Za-z0-9_-])pull_request_target(?![A-Za-z0-9_-])")

# The syntax example lists these access levels and no others.
LEVELS = {
    "actions": {"read", "write", "none"},
    "artifact-metadata": {"read", "write", "none"},
    "attestations": {"read", "write", "none"},
    "checks": {"read", "write", "none"},
    "code-quality": {"read", "write", "none"},
    "contents": {"read", "write", "none"},
    "copilot-requests": {"write", "none"},
    "deployments": {"read", "write", "none"},
    "id-token": {"write", "none"},
    "issues": {"read", "write", "none"},
    "discussions": {"read", "write", "none"},
    "packages": {"read", "write", "none"},
    "pages": {"read", "write", "none"},
    "pull-requests": {"read", "write", "none"},
    "security-events": {"read", "write", "none"},
    "statuses": {"read", "write", "none"},
    "vulnerability-alerts": {"read", "none"},
}


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
    def __init__(self, indent: int, role: str, name: str | None = None, record: dict | None = None) -> None:
        self.indent = indent
        self.role = role
        self.name = name
        self.record = record


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


def mentions_target(value: str) -> bool:
    return EVENT_RE.search(value) is not None


def parse_block(value: str, has: bool, children: list[Line], line_no: int) -> dict:
    if has:
        shown = unquote(value)
        if shown in {"read-all", "write-all"}:
            return {"form": shown, "line": line_no, "scopes": [], "duplicate": []}
        if shown == "{}":
            return {"form": "none", "line": line_no, "scopes": [], "duplicate": []}
        if shown.startswith("{") or shown.startswith("["):
            return {"form": "flow", "line": line_no, "scopes": [], "duplicate": []}
        return {"form": "scalar", "line": line_no, "scopes": [], "duplicate": []}
    if not children:
        return {"form": "empty", "line": line_no, "scopes": [], "duplicate": []}
    base = children[0].indent
    scopes = []
    seen: set[str] = set()
    duplicate: list[str] = []
    for child in children:
        if child.indent != base or child.text.startswith("-"):
            fail(f"permissions on line {line_no} is not a flat map")
        split = split_key(child.text)
        if split is None:
            fail(f"unparsed line {child.number}")
        key, raw_access, access_present = split
        if not access_present or is_block_value(raw_access):
            fail(f"permissions on line {line_no} is not a flat map")
        access = unquote(raw_access)
        if key in seen and key not in duplicate:
            duplicate.append(key)
        seen.add(key)
        allowed = LEVELS.get(key)
        if any(char.isspace() for char in access) or access == "":
            scopes.append({"name": key, "access": access, "ok": False, "reason": "level"})
        elif allowed is None:
            scopes.append({"name": key, "access": access, "ok": False, "reason": "unknown"})
        elif access not in allowed:
            scopes.append({"name": key, "access": access, "ok": False, "reason": "level"})
        else:
            scopes.append({"name": key, "access": access, "ok": True, "reason": ""})
    return {"form": "map", "line": line_no, "scopes": scopes, "duplicate": duplicate}


def parse_lines(lines: list[Line]) -> dict:
    stack = [Frame(-1, "root")]
    workflow: list[dict] = []
    jobs: list[dict] = []
    skipped = 0
    target = False
    index = 0

    def take_children(start: int, indent: int, has: bool) -> tuple[list[Line], int]:
        if has:
            return [], start
        children: list[Line] = []
        while start < len(lines) and lines[start].indent > indent:
            children.append(lines[start])
            start += 1
        return children, start

    while index < len(lines):
        line = lines[index]
        while stack[-1].indent >= line.indent:
            stack.pop()
        if line.text.startswith("-"):
            body = line.text[1:].strip()
            parent = stack[-1]
            if parent.role == "on" and body == "pull_request_target":
                target = True
            if parent.role == "steps":
                stack.append(Frame(line.indent, "step"))
                if body and split_key(body) is None and ":" in body:
                    fail(f"unparsed line {line.number}")
            elif body and split_key(body) is not None:
                stack.append(Frame(line.indent, "item"))
            elif body and ":" in body:
                fail(f"unparsed line {line.number}")
            if body and split_key(body) is not None and stack[-1].role in {"step", "item"}:
                # A key on the dash line is handled like any other key, but the
                # permissions collector below only runs for full lines. Replay
                # that key when it is permissions.
                split = split_key(body)
                assert split is not None
                key, value, has = split
                if key == "permissions":
                    children, index = take_children(index + 1, line.indent, has)
                    if stack[-2].role in {"root", "job"}:
                        block = parse_block(value, has, children, line.number)
                        attach_block(stack[-2], block, workflow)
                    else:
                        skipped += 1
                    continue
            index += 1
            continue

        split = split_key(line.text)
        if split is None:
            fail(f"unparsed line {line.number}")
        key, value, has = split
        parent = stack[-1]
        if parent.role == "root" and key == "on" and has and mentions_target(value):
            target = True
        if parent.role == "on" and key == "pull_request_target":
            target = True
        if key == "permissions":
            children, index = take_children(index + 1, line.indent, has)
            if parent.role in {"root", "job"}:
                block = parse_block(value, has, children, line.number)
                attach_block(parent, block, workflow)
            else:
                skipped += 1
            continue
        if parent.role == "root" and key == "jobs":
            if has:
                fail(f"jobs on line {line.number} is not a block")
            stack.append(Frame(line.indent, "jobs"))
        elif parent.role == "jobs":
            if has:
                fail(f"job {key} on line {line.number} is not a block")
            record = {"name": key, "block": None, "duplicate_job": False}
            if any(item["name"] == key for item in jobs):
                record["duplicate_job"] = True
            jobs.append(record)
            stack.append(Frame(line.indent, "job", key, record))
        elif parent.role == "job" and key == "steps":
            if has:
                fail(f"steps on line {line.number} is not a block")
            stack.append(Frame(line.indent, "steps"))
        elif parent.role == "root" and key == "on" and not has:
            stack.append(Frame(line.indent, "on"))
        elif not has:
            stack.append(Frame(line.indent, "map"))
        index += 1

    return {
        "workflow": workflow,
        "jobs": jobs,
        "skipped": skipped,
        "pull_request_target": target,
    }


def attach_block(parent: Frame, block: dict, workflow: list[dict]) -> None:
    if parent.role == "root":
        workflow.append(block)
        return
    record = parent.record
    if record is None:
        fail("permissions key is outside a workflow or a job")
    if record["block"] is None:
        record["block"] = block
        return
    record["block"]["duplicate_key"] = True
    record["block"]["scopes"].extend(block["scopes"])
    record["block"]["duplicate"].extend(block["duplicate"])


def block_ok(block: dict) -> bool:
    if block["form"] not in {"read-all", "write-all", "none", "map"}:
        return False
    if block["duplicate"] or block.get("duplicate_key"):
        return False
    return all(scope["ok"] for scope in block["scopes"])


def format_block(prefix: str, block: dict, rows: list[str]) -> None:
    rows.append(f"{prefix}form={block['form']}")
    rows.append(f"permissions_line={block['line']}")
    for scope in block["scopes"]:
        rows.append(f"scope={scope['name']}")
        rows.append(f"access={scope['access']}")
        rows.append(f"scope_ok={'yes' if scope['ok'] else 'no'}")
        if scope["reason"]:
            rows.append(f"reason={scope['reason']}")
    for name in block["duplicate"]:
        rows.append(f"duplicate={name}")
    if block["form"] == "map":
        rows.append("unspecified=none")


def format_report(parsed: dict) -> str:
    ok = True
    workflow = parsed["workflow"]
    if len(workflow) > 1:
        ok = False
    for block in workflow:
        if not block_ok(block):
            ok = False
    for job in parsed["jobs"]:
        if job["duplicate_job"]:
            ok = False
        if job["block"] is not None and not block_ok(job["block"]):
            ok = False
    rows = [
        f"ok={'yes' if ok else 'no'}",
        f"pull_request_target={'yes' if parsed['pull_request_target'] else 'no'}",
        f"skipped_permissions={parsed['skipped']}",
        f"duplicate_workflow={'yes' if len(workflow) > 1 else 'no'}",
    ]
    if not workflow:
        rows.append("workflow_form=absent")
    else:
        for block in workflow:
            format_block("workflow_", block, rows)
    for job in parsed["jobs"]:
        rows.append(f"job={job['name']}")
        if job["duplicate_job"]:
            rows.append("duplicate_job=yes")
        if job["block"] is None:
            rows.append("job_form=absent")
        else:
            format_block("job_", job["block"], rows)
    rows.append(f"jobs={len(parsed['jobs'])}")
    return "\n".join(rows)


def report_text(text: str) -> str:
    return format_report(parse_lines(logical_lines(text)))


def self_test() -> None:
    fixture = (Path(__file__).resolve().parents[1] / "assets" / "workflow.yml").read_text(encoding="utf-8")
    report = report_text(fixture)
    for line in (
        "ok=yes",
        "pull_request_target=no",
        "duplicate_workflow=no",
        "workflow_form=map",
        "scope=contents",
        "access=read",
        "scope_ok=yes",
        "unspecified=none",
        "job=test",
        "job_form=absent",
        "job=release",
        "job_form=map",
        "scope=id-token",
        "access=write",
        "jobs=2",
    ):
        if line not in report.splitlines():
            fail(f"self-test missing {line}")
    if report.splitlines().count("unspecified=none") != 2:
        fail("self-test printed unspecified=none the wrong number of times")

    read_all = report_text("permissions: read-all\njobs:\n  test:\n    steps:\n      - run: echo hi\n")
    if "workflow_form=read-all" not in read_all or "unspecified=none" in read_all:
        fail("self-test treated read-all as a scope map")

    empty = report_text("permissions: {}\n")
    if "workflow_form=none" not in empty or not empty.startswith("ok=yes"):
        fail("self-test rejected permissions: {}")

    level = report_text("jobs:\n  release:\n    permissions:\n      id-token: read\n")
    if "scope_ok=no" not in level or "reason=level" not in level or not level.startswith("ok=no"):
        fail("self-test accepted id-token: read")

    unknown = report_text("permissions:\n  metadata: read\n")
    if "reason=unknown" not in unknown or not unknown.startswith("ok=no"):
        fail("self-test accepted an unknown scope")

    alerts = report_text("permissions:\n  vulnerability-alerts: write\n")
    if "reason=level" not in alerts:
        fail("self-test accepted vulnerability-alerts: write")

    flow = report_text("permissions: {contents: read}\n")
    if "workflow_form=flow" not in flow or not flow.startswith("ok=no"):
        fail("self-test read a flow map")

    target = report_text("on:\n  pull_request_target:\npermissions: read-all\n")
    if "pull_request_target=yes" not in target:
        fail("self-test missed pull_request_target")

    listed = report_text("on: [push, pull_request_target]\npermissions: write-all\n")
    if "pull_request_target=yes" not in listed or "workflow_form=write-all" not in listed:
        fail("self-test missed a flow-list pull_request_target")

    hidden = report_text(
        "jobs:\n  test:\n    steps:\n      - run: |\n          echo permissions:\n            contents: write\n"
    )
    if "scope=contents" in hidden or "workflow_form=absent" not in hidden:
        fail("self-test read permissions inside a block scalar")

    skipped = report_text(
        "jobs:\n  test:\n    steps:\n      - name: odd\n        permissions:\n          contents: write\n"
    )
    if "skipped_permissions=1" not in skipped or "scope=contents" in skipped:
        fail("self-test treated a step key as a token scope")

    duplicate = report_text("permissions:\n  contents: read\n  contents: write\n")
    if "duplicate=contents" not in duplicate or not duplicate.startswith("ok=no"):
        fail("self-test hid a duplicate scope")
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
