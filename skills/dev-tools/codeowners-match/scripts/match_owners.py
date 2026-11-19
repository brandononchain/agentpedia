#!/usr/bin/env python3
"""Report the last CODEOWNERS pattern that matches each path.

Pattern rules follow the gitignore format GitHub cites, minus the three
forms GitHub says do not work in CODEOWNERS: negation, character ranges,
and a backslash that tries to make a leading # into a pattern.
https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners
https://git-scm.com/docs/gitignore#_pattern_format
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

USER_RE = re.compile(
    r"^@[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?"
    r"(?:/[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?)?$"
)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
SIZE_LIMIT = 3_000_000

Token = tuple[str, str]


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(2)


def merge_lits(tokens: list[Token]) -> list[Token]:
    merged: list[Token] = []
    for kind, value in tokens:
        if kind == "lit" and merged and merged[-1][0] == "lit":
            merged[-1] = ("lit", merged[-1][1] + value)
        else:
            merged.append((kind, value))
    return merged


def lex(pattern: str) -> tuple[list[list[Token]] | None, str | None]:
    segments: list[list[Token]] = [[]]
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if char == "\\":
            if index + 1 >= len(pattern):
                return None, "trailing-escape"
            segments[-1].append(("lit", pattern[index + 1]))
            index += 2
            continue
        if char in "[]":
            return None, "character-range"
        if char == "/":
            segments.append([])
            index += 1
            continue
        if char == "*":
            segments[-1].append(("star", ""))
            index += 1
            continue
        if char == "?":
            segments[-1].append(("q", ""))
            index += 1
            continue
        segments[-1].append(("lit", char))
        index += 1
    normalized: list[list[Token]] = []
    for segment in segments:
        if len(segment) == 2 and segment[0][0] == "star" and segment[1][0] == "star":
            normalized.append([("globstar", "")])
        else:
            normalized.append(merge_lits(segment))
    return normalized, None


def prepare(raw: str) -> tuple[tuple[list[list[Token]], bool] | None, str | None]:
    if raw.startswith("!"):
        return None, "negation"
    if raw.startswith("\\#"):
        return None, "escaped-hash"
    directory = raw.endswith("/")
    pattern = raw[:-1] if directory else raw
    if pattern == "":
        return None, "empty"
    anchored = False
    if pattern.startswith("/"):
        anchored = True
        pattern = pattern[1:]
        if pattern == "":
            return None, "empty"
    tokens, error = lex(pattern)
    if error:
        return None, error
    if not tokens or any(segment == [] for segment in tokens):
        return None, "empty-segment"
    if not anchored and tokens[0] != [("globstar", "")]:
        if len(tokens) > 1:
            anchored = True
    if not anchored and tokens[0] != [("globstar", "")]:
        tokens = [[("globstar", "")]] + tokens
    last = tokens[-1]
    last_literal = bool(last) and all(token[0] == "lit" for token in last)
    descendants = directory or last_literal
    return (tokens, descendants), None


def segment_match(tokens: list[Token], text: str) -> bool:
    parts: list[str] = []
    for kind, value in tokens:
        if kind == "lit":
            parts.append(re.escape(value))
        elif kind == "star":
            parts.append("[^/]*")
        elif kind == "q":
            parts.append("[^/]")
        else:
            return False
    return re.fullmatch("".join(parts), text) is not None


def path_match(tokens: list[list[Token]], descendants: bool, path: str) -> bool:
    segments = path.split("/")

    def rec(token_index: int, path_index: int, seen: dict[tuple[int, int], bool]) -> bool:
        key = (token_index, path_index)
        if key in seen:
            return seen[key]
        if token_index == len(tokens):
            ok = path_index == len(segments) or (descendants and path_index < len(segments))
            seen[key] = ok
            return ok
        if tokens[token_index] == [("globstar", "")]:
            if token_index == len(tokens) - 1:
                seen[key] = True
                return True
            cursor = path_index
            while True:
                if rec(token_index + 1, cursor, seen):
                    seen[key] = True
                    return True
                if cursor == len(segments):
                    seen[key] = False
                    return False
                cursor += 1
        if path_index >= len(segments) or not segment_match(tokens[token_index], segments[path_index]):
            seen[key] = False
            return False
        ok = rec(token_index + 1, path_index + 1, seen)
        seen[key] = ok
        return ok

    return rec(0, 0, {})


def owner_ok(token: str) -> bool:
    if token.startswith("@"):
        return USER_RE.fullmatch(token) is not None
    return EMAIL_RE.fullmatch(token) is not None


def norm_path(raw: str) -> str | None:
    text = raw.strip()
    if text.startswith("./"):
        text = text[2:]
    if text.startswith("/"):
        text = text[1:]
    if text.endswith("/"):
        text = text[:-1]
    if text == "" or "\\" in text:
        return None
    parts = text.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return None
    return "/".join(parts)


def load_rules(text: str) -> tuple[list[tuple[int, str, list[str], list[list[Token]], bool]], list[tuple[int, str, str]]]:
    rules = []
    skipped = []
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if line == "" or line.startswith("#"):
            continue
        if " #" in line:
            line = line.split(" #", 1)[0].rstrip()
        parts = line.split()
        if not parts:
            continue
        pattern = parts[0]
        owners = parts[1:]
        if owners and not all(owner_ok(owner) for owner in owners):
            skipped.append((number, "owner", pattern))
            continue
        prepared, error = prepare(pattern)
        if error or prepared is None:
            skipped.append((number, error or "pattern", pattern))
            continue
        tokens, descendants = prepared
        rules.append((number, pattern, owners, tokens, descendants))
    return rules, skipped


def match_path(rules: list[tuple[int, str, list[str], list[list[Token]], bool]], path: str) -> tuple[int, str, list[str]] | None:
    winner = None
    for number, pattern, owners, tokens, descendants in rules:
        if path_match(tokens, descendants, path):
            winner = (number, pattern, owners)
    return winner


def render_path(path: str, winner: tuple[int, str, list[str]] | None) -> list[str]:
    if winner is None:
        return [f"path={path}", "matched=no"]
    number, pattern, owners = winner
    return [
        f"path={path}",
        "matched=yes",
        f"line={number}",
        f"pattern={pattern}",
        f"owners={' '.join(owners)}",
        f"owners_empty={'no' if owners else 'yes'}",
    ]


def evaluate(codeowners: str, paths: list[str]) -> list[str]:
    rules, skipped = load_rules(codeowners)
    lines: list[str] = []
    kept = 0
    for raw in paths:
        if raw.strip() == "" or raw.strip().startswith("#"):
            continue
        path = norm_path(raw)
        if path is None:
            fail(f"path is not a repo-relative file: {raw.strip()}")
        kept += 1
        lines.extend(render_path(path, match_path(rules, path)))
    if kept == 0:
        fail("no paths")
    for number, reason, pattern in skipped:
        lines.append(f"skip line={number} reason={reason} pattern={pattern}")
    lines.append(f"paths={kept}")
    lines.append(f"skipped={len(skipped)}")
    return lines


def self_test() -> None:
    github = "\n".join(
        [
            "# comment",
            "* @global-owner1 @global-owner2",
            "*.js @js-owner #This is an inline comment.",
            "*.go docs@example.com",
            "*.txt @octo-org/octocats",
            "/build/logs/ @doctocat",
            "docs/* docs@example.com",
            "apps/ @octocat",
            "/docs/ @doctocat",
            "/scripts/ @doctocat @octocat",
            "**/logs @octocat",
            "/apps/ @octocat",
            "/apps/github",
            "/apps/ @octocat",
            "/apps/github @doctocat",
            "!dist/ @nope",
            "*.[ch] @c-owner",
        ]
    )
    paths = [
        "src/app.js",
        "lib/main.go",
        "notes.txt",
        "build/logs/out.txt",
        "other/build/logs/a.txt",
        "docs/getting-started.md",
        "docs/build-app/troubleshooting.md",
        "src/apps/sub/main.ts",
        "scripts/run.sh",
        "deeply/nested/logs/a.txt",
        "apps/web/readme.md",
        "apps/github/readme.md",
        "README.md",
        "Docs/A.md",
    ]
    lines = evaluate(github, paths)
    expect_owner(lines, "src/app.js", "*.js", "@js-owner", "no")
    expect_owner(lines, "lib/main.go", "*.go", "docs@example.com", "no")
    expect_owner(lines, "notes.txt", "*.txt", "@octo-org/octocats", "no")
    expect_owner(lines, "build/logs/out.txt", "**/logs", "@octocat", "no")
    expect_owner(lines, "other/build/logs/a.txt", "**/logs", "@octocat", "no")
    expect_owner(lines, "docs/getting-started.md", "/docs/", "@doctocat", "no")
    expect_owner(lines, "docs/build-app/troubleshooting.md", "/docs/", "@doctocat", "no")
    expect_owner(lines, "src/apps/sub/main.ts", "apps/", "@octocat", "no")
    expect_owner(lines, "scripts/run.sh", "/scripts/", "@doctocat @octocat", "no")
    expect_owner(lines, "deeply/nested/logs/a.txt", "**/logs", "@octocat", "no")
    expect_owner(lines, "apps/web/readme.md", "/apps/", "@octocat", "no")
    expect_owner(lines, "apps/github/readme.md", "/apps/github", "@doctocat", "no")
    expect_owner(lines, "README.md", "*", "@global-owner1 @global-owner2", "no")
    expect_owner(lines, "Docs/A.md", "*", "@global-owner1 @global-owner2", "no")
    if "skip line=16 reason=negation pattern=!dist/" not in lines:
        fail("self-test missed negation skip: " + " | ".join(lines))
    if "skip line=17 reason=character-range pattern=*.[ch]" not in lines:
        fail("self-test missed character range: " + " | ".join(lines))
    empty = evaluate("* @root\n/apps/github\n", ["apps/github/readme.md"])
    expect_owner(empty, "apps/github/readme.md", "/apps/github", "", "yes")
    question = evaluate("file?.txt @one\n", ["fileX.txt", "fileXY.txt", "dir/fileX.txt"])
    expect_owner(question, "fileX.txt", "file?.txt", "@one", "no")
    expect_owner(question, "dir/fileX.txt", "file?.txt", "@one", "no")
    block = "\n".join(question)
    if "path=fileXY.txt\nmatched=no" not in block:
        fail("self-test ? matched too much: " + block)
    nested = evaluate("a/**/b @owner\n", ["a/b", "a/x/y/b/file", "q/a/b"])
    expect_owner(nested, "a/b", "a/**/b", "@owner", "no")
    expect_owner(nested, "a/x/y/b/file", "a/**/b", "@owner", "no")
    joined = "\n".join(nested)
    if "path=q/a/b\nmatched=no" not in joined:
        fail("self-test ** matched outside the anchor: " + joined)
    print("self-test=ok")


def expect_owner(lines: list[str], path: str, pattern: str, owners: str, empty: str) -> None:
    try:
        start = lines.index(f"path={path}")
    except ValueError:
        fail(f"self-test missing {path}")
    window = lines[start : start + 6]
    wanted = [
        f"path={path}",
        "matched=yes",
        f"pattern={pattern}",
        f"owners={owners}",
        f"owners_empty={empty}",
    ]
    for item in wanted:
        if item not in window:
            fail(f"self-test {path} missing {item}: {window}")


def read_list(path: Path) -> list[str]:
    if not path.is_file():
        fail(f"not a file: {path}")
    return path.read_text(encoding="utf-8").splitlines()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codeowners", type=Path)
    parser.add_argument("--paths", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if args.codeowners is None or args.paths is None:
        fail("pass --codeowners and --paths, or --self-test")
    if not args.codeowners.is_file():
        fail(f"not a file: {args.codeowners}")
    if args.codeowners.stat().st_size >= SIZE_LIMIT:
        fail(f"CODEOWNERS is {args.codeowners.stat().st_size} bytes; this script stops at {SIZE_LIMIT}")
    print("\n".join(evaluate(args.codeowners.read_text(encoding="utf-8"), read_list(args.paths))))


if __name__ == "__main__":
    main()
