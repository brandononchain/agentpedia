"""First-seen dates for high and critical findings.

The date is recorded once. A later build does not move it, so the grace
period cannot be reset by rewriting the entry around the same evidence.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from audit import DEFAULT_GRACE_DAYS
from audit.models import Finding

SCHEMA = "agentpedia.audit-grace.v1"


def ledger_path(root: Path) -> Path:
    return root / "data" / "audit-grace.json"


def empty_ledger() -> dict:
    return {"schema": SCHEMA, "graceDays": DEFAULT_GRACE_DAYS, "findings": {}}


def load_ledger(root: Path) -> dict:
    path = ledger_path(root)
    if not path.is_file():
        return empty_ledger()
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return empty_ledger()
    data.setdefault("schema", SCHEMA)
    data.setdefault("graceDays", DEFAULT_GRACE_DAYS)
    findings = data.get("findings")
    if not isinstance(findings, dict):
        data["findings"] = {}
    return data


def grace_days(ledger: dict) -> int:
    override = os.environ.get("AGENTPEDIA_AUDIT_GRACE_DAYS", "").strip()
    if override:
        value = int(override)
        if value < 0:
            raise ValueError("AGENTPEDIA_AUDIT_GRACE_DAYS must be >= 0")
        return value
    value = int(ledger.get("graceDays") or DEFAULT_GRACE_DAYS)
    return value


def fingerprint(entry_id: str, finding: Finding) -> str:
    norm = " ".join(finding.evidence.lower().split())
    digest = hashlib.sha256(f"{finding.rule_id}\n{finding.path}\n{norm}".encode()).hexdigest()[:20]
    return f"{entry_id}|{digest}"


def remember(ledger: dict, entry_id: str, findings: list[Finding], today: str) -> None:
    store = ledger.setdefault("findings", {})
    for finding in findings:
        if finding.severity not in {"high", "critical"}:
            continue
        key = fingerprint(entry_id, finding)
        if key in store:
            continue
        store[key] = {
            "entryId": entry_id,
            "ruleId": finding.rule_id,
            "path": finding.path,
            "firstSeen": today,
            "severity": finding.severity,
        }


def first_seen(ledger: dict, entry_id: str, finding: Finding) -> str | None:
    item = ledger.get("findings", {}).get(fingerprint(entry_id, finding))
    if isinstance(item, dict) and item.get("firstSeen"):
        return str(item["firstSeen"])
    return None


def save_ledger(root: Path, ledger: dict) -> bool:
    path = ledger_path(root)
    payload = {
        "schema": SCHEMA,
        "graceDays": int(ledger.get("graceDays") or DEFAULT_GRACE_DAYS),
        "findings": dict(sorted((ledger.get("findings") or {}).items())),
    }
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if path.is_file() and path.read_text(encoding="utf-8") == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True
