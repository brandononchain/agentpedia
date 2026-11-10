from __future__ import annotations

import json
import sys

from skill_lint.models import Finding, LintResult


def render_text(result: LintResult, color: bool = False) -> str:
    lines: list[str] = []
    if result.extra_findings:
        lines.append(_skill_header("(scan)"))
        for finding in result.extra_findings:
            lines.extend(_format_finding(finding, color))
        lines.append("")
    for skill in result.skills:
        title = skill.name or "(unnamed)"
        lines.append(_skill_header(f"{title}  {skill.path}"))
        if not skill.findings:
            lines.append("  ok  no findings")
        else:
            for finding in skill.findings:
                lines.extend(_format_finding(finding, color))
        lines.append("")
    lines.append(
        f"{len(result.skills)} skill(s) scanned, "
        f"{result.error_count} error(s), "
        f"{result.warn_count} warning(s), "
        f"{result.info_count} info"
    )
    return "\n".join(lines).rstrip() + "\n"


def render_json(result: LintResult) -> str:
    return json.dumps(result.to_dict(), indent=2) + "\n"


def _skill_header(text: str) -> str:
    return text


def _format_finding(finding: Finding, color: bool) -> list[str]:
    loc = f"{finding.rule_id}"
    if finding.line:
        loc = f"{finding.rule_id}:{finding.line}"
    severity = finding.severity
    if color and sys.stdout.isatty():
        palette = {"error": "\033[31m", "warn": "\033[33m", "info": "\033[36m"}
        reset = "\033[0m"
        severity = f"{palette.get(finding.severity, '')}{finding.severity}{reset}"
    return [
        f"  {severity:<5} {loc}  {finding.message}",
        f"        fix: {finding.hint}",
    ]
