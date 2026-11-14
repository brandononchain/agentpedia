from __future__ import annotations

import argparse
import sys
from pathlib import Path

from skill_lint import __version__
from skill_lint.discover import discover
from skill_lint.frontmatter import split_frontmatter
from skill_lint.models import Finding, LintResult
from skill_lint.report import render_json, render_text
from skill_lint.rules import lint_skill
from skill_lint.shelf_case import category_files_for, findings_for_category, findings_for_subshelf


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skill-lint",
        description="Lint Agent Skills (SKILL.md files or folders of skill folders).",
    )
    parser.add_argument("path", help="Path to a SKILL.md file, a skill folder, or a folder of skills")
    parser.add_argument("--json", action="store_true", help="Print findings as JSON")
    parser.add_argument("--version", action="version", version=f"skill-lint {__version__}")
    return parser


def lint_path(path: Path) -> LintResult:
    result = LintResult()
    if not path.exists():
        result.extra_findings.append(
            Finding(
                rule_id="scan.path.missing",
                severity="error",
                message=f"path does not exist: {path}",
                hint="Pass a SKILL.md file or a directory that contains skill folders.",
                path=str(path),
            )
        )
        return result
    try:
        files = discover(path)
    except FileNotFoundError:
        result.extra_findings.append(
            Finding(
                rule_id="scan.path.missing",
                severity="error",
                message=f"path does not exist: {path}",
                hint="Pass a SKILL.md file or a directory that contains skill folders.",
                path=str(path),
            )
        )
        return result
    if not files:
        result.extra_findings.append(
            Finding(
                rule_id="scan.skill.not-found",
                severity="error",
                message=f"no SKILL.md files found under {path}",
                hint="Point at a skill folder (containing SKILL.md) or a parent folder of skill folders.",
                path=str(path),
            )
        )
        return result
    for file in files:
        result.skills.append(lint_skill(file))
        front = split_frontmatter(file.read_text(encoding="utf-8"))
        result.extra_findings.extend(findings_for_subshelf(file, front.fields))
    for meta in category_files_for(files):
        result.extra_findings.extend(findings_for_category(meta))
    return result


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = lint_path(Path(args.path))
    output = render_json(result) if args.json else render_text(result, color=not args.json)
    sys.stdout.write(output)
    return 1 if result.error_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
