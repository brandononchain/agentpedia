"""Score, grade, and the Listed gate.

score = max(0, 100 - sum(weight × count))
weights: critical 40, high 18, medium 8, low 3, info 1

Grade F if any finding is critical or the score is below 60.
Otherwise D below 70, C below 80, B below 90, and A from 90.

Status is on-hold when the grade is F, any finding is critical, or a high
finding is past its grace period. High findings inside the grace period are
a warning. Anything else passed.
"""

from __future__ import annotations

from datetime import date, timedelta

from audit import AUDIT_DAYS, WEIGHTS
from audit.models import Finding

SEVERITIES = ("critical", "high", "medium", "low", "info")


def counts(findings: list[Finding]) -> dict[str, int]:
    tally = {name: 0 for name in SEVERITIES}
    for finding in findings:
        tally[finding.severity] = tally.get(finding.severity, 0) + 1
    return tally


def score_for(findings: list[Finding]) -> int:
    total = 100
    tally = counts(findings)
    for name, weight in WEIGHTS.items():
        total -= tally.get(name, 0) * weight
    return max(0, total)


def grade_for(score: int, findings: list[Finding]) -> str:
    if any(finding.severity == "critical" for finding in findings) or score < 60:
        return "F"
    if score < 70:
        return "D"
    if score < 80:
        return "C"
    if score < 90:
        return "B"
    return "A"


def parse_iso(value: str) -> date:
    year, month, day = (int(part) for part in value.split("-"))
    return date(year, month, day)


def days_remaining(first_seen: str, today: str, grace_days: int) -> int:
    return grace_days - (parse_iso(today) - parse_iso(first_seen)).days


def expires_on(audited_at: str) -> str:
    return (parse_iso(audited_at) + timedelta(days=AUDIT_DAYS)).isoformat()


def classify(findings: list[Finding], *, high_expired: bool, grace_days_left: int | None) -> tuple[str, str]:
    tally = counts(findings)
    score = score_for(findings)
    grade = grade_for(score, findings)
    if tally["critical"]:
        return "on-hold", "On hold. The audit found a critical finding."
    if grade == "F":
        return "on-hold", f"On hold. The score is {score}, grade F."
    if tally["high"] and high_expired:
        return "on-hold", "On hold. A high finding is past the grace period."
    if tally["high"]:
        left = 0 if grace_days_left is None else grace_days_left
        day = "day" if left == 1 else "days"
        return "warning", f"Warning. High findings are inside the grace period, with {left} {day} left."
    return "passed", "Passed. The static audit found no critical or high findings."
