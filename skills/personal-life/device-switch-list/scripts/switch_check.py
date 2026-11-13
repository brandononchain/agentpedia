#!/usr/bin/env python3
"""Check a device-move list. Does not sign in or print a code."""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

KINDS = {"login", "authenticator", "files", "subscription", "other"}
SECRETISH_RE = re.compile(
    r"(?i)(?:\b(?:password|passcode|passphrase|api[_-]?key|secret|token|otp|seed)\b\s*[:=]\s*\S+"
    r"|-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----)"
)
DIGITS_RE = re.compile(r"\d{4,}")


def fail(message: str) -> None:
    raise SystemExit(message)


def one_line(value: str, row_number: int, label: str) -> str:
    if "\t" in value or "\n" in value or "\r" in value:
        fail(f"row {row_number} {label} must be one line")
    return value


def looks_secret(value: str) -> bool:
    if SECRETISH_RE.search(value):
        return True
    return bool(DIGITS_RE.fullmatch(value.strip()))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python3 scripts/switch_check.py <csv>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    rows = []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        if not {"account", "kind", "must_move", "where"} <= fields:
            fail("csv needs account, kind, must_move, and where columns")
        for index, row in enumerate(reader, start=2):
            account = one_line((row.get("account") or "").strip(), index, "account")
            kind = one_line((row.get("kind") or "").strip(), index, "kind").casefold()
            must_move = one_line((row.get("must_move") or "").strip(), index, "must_move").casefold()
            where = one_line((row.get("where") or "").strip(), index, "where")
            if account == "" and kind == "" and must_move == "" and where == "":
                continue
            flags: list[str] = []
            if account == "":
                flags.append("incomplete")
            if kind not in KINDS:
                flags.append("bad-kind")
            if must_move not in {"yes", "no"}:
                flags.append("bad-must-move")
            if must_move == "yes" and where == "":
                flags.append("missing-where")
            if looks_secret(account) or looks_secret(where):
                flags.append("secretish")
            rows.append((must_move, kind, account, where, flags or ["ok"]))

    rows.sort(key=lambda item: (item[0] != "yes", item[1], item[2].casefold()))

    def count(flag: str) -> int:
        return sum(1 for *_rest, flags in rows if flag in flags)

    must_move = sum(1 for flag, *_rest in rows if flag == "yes")
    ready = bool(rows) and all(flags == ["ok"] for *_rest, flags in rows)
    lines = [
        f"rows={len(rows)}",
        f"must_move={must_move}",
        f"missing_where={count('missing-where')}",
        f"secretish={count('secretish')}",
        f"bad_kind={count('bad-kind')}",
        f"ready={'yes' if ready else 'no'}",
        "must_move\tkind\taccount\twhere\tflags",
    ]
    for move, kind, account, where, flags in rows:
        lines.append("\t".join([move, kind, account, where, ",".join(flags)]))
    sys.stdout.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
