#!/usr/bin/env python3
"""Flag token-shaped strings. Prints the line and the kind, never the secret."""

from __future__ import annotations

import re
import sys
from pathlib import Path

PATTERNS = [
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("github-token", re.compile(r"\bghp_[A-Za-z0-9]{20,}\b")),
    ("openai-key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("private-key", re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")),
]
TOKEN_RE = re.compile(r"[A-Za-z0-9+/=_-]{24,}")


def high_entropy(token: str) -> bool:
    if len(token) < 24 or not TOKEN_RE.fullmatch(token):
        return False
    classes = sum(
        [
            any(char.islower() for char in token),
            any(char.isupper() for char in token),
            any(char.isdigit() for char in token),
        ]
    )
    return classes >= 2 and len(set(token)) >= 12


def scan(text: str) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    seen: set[tuple[int, str]] = set()
    for number, line in enumerate(text.splitlines(), start=1):
        kinds = [name for name, pattern in PATTERNS if pattern.search(line)]
        if not kinds and any(high_entropy(token) for token in TOKEN_RE.findall(line)):
            kinds = ["high-entropy"]
        for kind in kinds:
            key = (number, kind)
            if key not in seen:
                seen.add(key)
                found.append(key)
    return found


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python3 scripts/scan_text.py <file>", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    findings = scan(path.read_text(encoding="utf-8", errors="replace"))
    for number, kind in findings:
        print(f"{number}\t{kind}")
    print(f"findings={len(findings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
