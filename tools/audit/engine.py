"""Scan one skill or agent directory and build the public audit record."""

from __future__ import annotations

from pathlib import Path

from audit import AUDITOR, RULESET_VERSION
from audit.digest import lock_hash
from audit.grace import first_seen, grace_days
from audit.models import Finding
from audit.osv import DisabledOsv, OsvLookup, lookup_from_env
from audit.rules import rule_catalog, scan_bytes, scan_supply
from audit.scoring import classify, counts, days_remaining, expires_on, grade_for, score_for

SKIP_DIRS = {".git", "__pycache__", "__pypackages__", ".pytest_cache"}

STAGES = [
    {
        "id": "static",
        "phase": 1,
        "title": "Static analysis",
        "status": "complete",
        "detail": "Rules S, C, and D ran on this tree. No code from the entry was executed.",
    },
    {
        "id": "sandbox",
        "phase": 2,
        "title": "Sandbox run",
        "status": "not-run",
        "detail": "Design hook. A later phase runs the entry with no network and canary credentials.",
    },
    {
        "id": "redteam",
        "phase": 3,
        "title": "Prompt-injection red team",
        "status": "not-run",
        "detail": "Design hook. A later phase sends hostile text at the entry against mock tools.",
    },
    {
        "id": "manual",
        "phase": 4,
        "title": "Manual review",
        "status": "not-run",
        "detail": "Design hook. A later phase requires a reviewer who is not the entry's author.",
    },
]


def audit_directory(directory: Path, lookup: OsvLookup | None = None) -> tuple[list[Finding], str, str]:
    """Return findings, the skills-lock hash, and the CVE lookup state."""
    findings: list[Finding] = []
    if directory.is_dir():
        for path in sorted(directory.rglob("*"), key=lambda item: item.relative_to(directory).as_posix()):
            if not path.is_file():
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            rel = path.relative_to(directory).as_posix()
            try:
                data = path.read_bytes()
            except OSError:
                continue
            findings.extend(scan_bytes(rel, data))
        findings.extend(scan_supply(directory))
    client = lookup if lookup is not None else lookup_from_env()
    cve = "disabled"
    if not isinstance(client, DisabledOsv):
        cve = "stub"
        try:
            client.query([])
        except NotImplementedError:
            cve = "stub"
    deduped: list[Finding] = []
    seen: set[tuple[str, str, int, str]] = set()
    for finding in findings:
        key = (finding.rule_id, finding.path, finding.line, finding.evidence)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(finding)
    deduped.sort(key=lambda item: (item.path, item.line, item.rule_id))
    return deduped, lock_hash(directory) if directory.is_dir() else "", cve


def public_view(
    findings: list[Finding],
    *,
    lock: str,
    content_digest: str,
    commit: str,
    ledger: dict,
    entry_id: str,
    today: str,
    cve_lookup: str,
) -> dict:
    period = grace_days(ledger)
    high_left: list[int] = []
    missing = False
    for finding in findings:
        if finding.severity not in {"high", "critical"}:
            continue
        seen = first_seen(ledger, entry_id, finding)
        if seen is None:
            missing = True
            seen = today
        if finding.severity == "high":
            high_left.append(days_remaining(seen, today, period))
    expired = any(days < 0 for days in high_left)
    left = min(high_left) if high_left else None
    status, summary = classify(findings, high_expired=expired, grace_days_left=left)
    score = score_for(findings)
    grade = grade_for(score, findings)
    if missing and status == "warning":
        summary = summary + " The grace file does not yet record this finding."
    return {
        "score": score,
        "grade": grade,
        "status": status,
        "summary": summary,
        "graceDays": period,
        "graceDaysLeft": left if status == "warning" else None,
        "counts": counts(findings),
        "findings": [finding.to_dict() for finding in findings],
        "auditedCommit": commit,
        "contentDigest": content_digest,
        "lockHash": lock,
        "lockHashAlg": "skills-lock-v2",
        "rulesetVersion": RULESET_VERSION,
        "auditor": AUDITOR,
        "auditedAt": today,
        "expiresAt": expires_on(today),
        "cveLookup": cve_lookup,
        "stages": STAGES,
    }


def catalog_meta(views: list[dict]) -> dict:
    grades = {letter: 0 for letter in "ABCDF"}
    statuses = {"passed": 0, "warning": 0, "on-hold": 0}
    for view in views:
        grade = str(view.get("grade") or "")
        status = str(view.get("status") or "")
        if grade in grades:
            grades[grade] += 1
        if status in statuses:
            statuses[status] += 1
    return {
        "rulesetVersion": RULESET_VERSION,
        "auditor": AUDITOR,
        "weights": {"critical": 40, "high": 18, "medium": 8, "low": 3, "info": 1},
        "graceDays": 14,
        "auditDays": 90,
        "rules": rule_catalog(),
        "stats": {
            "entries": len(views),
            "grades": grades,
            "passed": statuses["passed"],
            "warning": statuses["warning"],
            "onHold": statuses["on-hold"],
        },
    }
