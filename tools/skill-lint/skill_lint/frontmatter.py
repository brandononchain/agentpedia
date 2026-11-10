from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Frontmatter:
    raw: str
    fields: dict[str, Any] = field(default_factory=dict)
    key_lines: dict[str, int] = field(default_factory=dict)
    parse_error: str | None = None
    present: bool = False
    body: str = ""
    body_start_line: int = 1


_KEY_RE = re.compile(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$")


def split_frontmatter(text: str) -> Frontmatter:
    """Parse YAML-ish SKILL.md frontmatter without a YAML dependency."""
    result = Frontmatter(raw="")
    if not text.startswith("---"):
        first = text.splitlines()[0] if text.strip() else ""
        if first.strip() == "---":
            pass
        else:
            result.body = text
            result.body_start_line = 1
            return result

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        result.body = text
        result.body_start_line = 1
        return result

    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        result.present = True
        result.parse_error = "frontmatter opening --- was not closed"
        result.body = text
        result.body_start_line = 1
        return result

    result.present = True
    fm_lines = lines[1:end]
    result.raw = "\n".join(fm_lines)
    result.body = "\n".join(lines[end + 1 :])
    if result.body:
        result.body = result.body + ("\n" if text.endswith("\n") and not result.body.endswith("\n") else "")
    result.body_start_line = end + 2  # 1-indexed line of first body line
    try:
        result.fields, result.key_lines = _parse_simple_yaml(fm_lines, line_offset=2)
    except ValueError as exc:
        result.parse_error = str(exc)
    return result


def _parse_simple_yaml(lines: list[str], line_offset: int) -> tuple[dict[str, Any], dict[str, int]]:
    data: dict[str, Any] = {}
    key_lines: dict[str, int] = {}
    i = 0
    while i < len(lines):
        raw = lines[i]
        if not raw.strip() or raw.strip().startswith("#"):
            i += 1
            continue
        if raw.startswith(" ") or raw.startswith("\t"):
            raise ValueError(f"unexpected indented line {i + line_offset}: {raw.strip()}")
        match = _KEY_RE.match(raw)
        if not match:
            raise ValueError(f"could not parse frontmatter line {i + line_offset}: {raw}")
        key, rest = match.group(1), match.group(2)
        key_lines[key] = i + line_offset
        rest = rest.strip()
        if rest in {">", ">-", "|", "|-"} or rest.startswith(">") or rest.startswith("|"):
            folded = rest.startswith(">")
            block: list[str] = []
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or lines[i].startswith("\t") or not lines[i].strip()):
                if not lines[i].strip():
                    block.append("")
                else:
                    block.append(lines[i].strip())
                i += 1
            if folded:
                data[key] = " ".join(part for part in block if part != "").replace("  ", " ").strip()
            else:
                data[key] = "\n".join(block).strip("\n")
            continue
        if rest == "":
            # nested map or empty
            nested: dict[str, str] = {}
            i += 1
            while i < len(lines) and (lines[i].startswith(" ") or lines[i].startswith("\t")):
                child = lines[i].strip()
                if not child or child.startswith("#"):
                    i += 1
                    continue
                child_match = _KEY_RE.match(child)
                if not child_match:
                    raise ValueError(f"could not parse nested key on line {i + line_offset}: {child}")
                nested[child_match.group(1)] = _unquote(child_match.group(2).strip())
                i += 1
            data[key] = nested if nested else ""
            continue
        data[key] = _unquote(rest)
        i += 1
    return data, key_lines


def _unquote(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        inner = value[1:-1]
        if value[0] == '"':
            return bytes(inner, "utf-8").decode("unicode_escape") if "\\" in inner else inner
        return inner
    if value.lower() in {"true", "false"}:
        return value  # keep as string; SKILL.md values are strings
    return value
