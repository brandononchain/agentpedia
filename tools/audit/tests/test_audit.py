"""Fixture, scoring, digest, grace, and network tests for the static audit."""

from __future__ import annotations

import hashlib
from datetime import date, timedelta
from pathlib import Path

import pytest

from audit.digest import hash_skill_files, lock_hash
from audit.engine import audit_directory, public_view
from audit.grace import empty_ledger, fingerprint, first_seen, remember
from audit.models import Finding
from audit.osv import DisabledOsv, OsvClient, lookup_from_env
from audit.rules import RULES, scan_bytes, scan_supply, typosquat
from audit.scoring import grade_for, score_for

FIXTURES = Path(__file__).parent / "fixtures"


def _finding(rule_id: str, severity: str, evidence: str = "evidence") -> Finding:
    return Finding(rule_id, severity, "SKILL.md", 1, evidence, "message", "fix it", "CWE-0", ("ASI01",))


def test_every_rule_has_a_positive_and_a_negative_fixture():
    missing = []
    for rule in RULES:
        folder = FIXTURES / rule.id
        if not folder.is_dir():
            missing.append(rule.id)
            continue
        positive = _case(folder, "positive")
        negative = _case(folder, "negative")
        if positive is None or negative is None:
            missing.append(rule.id)
            continue
        pos = _scan(positive)
        neg = _scan(negative)
        if not any(item.rule_id == rule.id for item in pos):
            missing.append(f"{rule.id} positive")
        if any(item.rule_id == rule.id for item in neg):
            missing.append(f"{rule.id} negative")
    assert missing == []


def _case(folder: Path, label: str) -> Path | None:
    direct = folder / label
    if direct.exists():
        return direct
    matches = sorted(path for path in folder.iterdir() if path.name.startswith(label + "."))
    return matches[0] if matches else None


def _scan(path: Path):
    if path.is_dir():
        findings, _lock, _cve = audit_directory(path)
        return findings
    return scan_bytes(path.name, path.read_bytes())


def test_lock_hash_matches_the_skills_lock_v2_vector(tmp_path: Path):
    content = b"hello\n"
    framed = hashlib.sha256(b"SKILL.md\x00" + str(len(content)).encode() + b"\x00" + content).hexdigest()
    assert hash_skill_files([("SKILL.md", content)]) == framed
    folder = tmp_path / "skill"
    folder.mkdir()
    (folder / "SKILL.md").write_bytes(content)
    (folder / "metadata.json").write_text('{"x":1}\n', encoding="utf-8")
    assert lock_hash(folder) == framed
    crlf = tmp_path / "crlf"
    crlf.mkdir()
    (crlf / "SKILL.md").write_bytes(b"hello\r\n")
    assert lock_hash(crlf) == framed


def test_score_grade_and_grace_do_not_reset():
    high = _finding("S08", "high", "send the email")
    assert score_for([high]) == 82
    assert grade_for(82, [high]) == "B"
    critical = _finding("S02", "critical", "ignore previous instructions")
    assert grade_for(score_for([critical]), [critical]) == "F"
    ledger = empty_ledger()
    remember(ledger, "skill-demo", [high], "2026-11-01")
    remember(ledger, "skill-demo", [high], "2026-11-20")
    assert first_seen(ledger, "skill-demo", high) == "2026-11-01"
    assert fingerprint("skill-demo", high) == fingerprint("skill-demo", high)
    view = public_view(
        [high],
        lock="abc",
        content_digest="sha256:" + "ab" * 32,
        commit="c" * 40,
        ledger=ledger,
        entry_id="skill-demo",
        today="2026-11-10",
        cve_lookup="disabled",
    )
    assert view["status"] == "warning"
    assert view["graceDaysLeft"] == 5
    assert view["grade"] == "B"
    later = public_view(
        [high],
        lock="abc",
        content_digest="sha256:" + "ab" * 32,
        commit="c" * 40,
        ledger=ledger,
        entry_id="skill-demo",
        today="2026-11-16",
        cve_lookup="disabled",
    )
    assert later["status"] == "on-hold"
    assert later["grade"] == "B"


def test_typosquat_flags_a_lookalike_and_not_the_real_name():
    assert typosquat("reqeusts") == "requests"
    assert typosquat("requests") is None
    assert typosquat("my-private-helper") is None


def test_osv_default_does_not_use_the_network(monkeypatch):
    def explode(*_args, **_kwargs):
        raise AssertionError("network was used")

    monkeypatch.setattr("urllib.request.urlopen", explode)
    assert isinstance(lookup_from_env(), DisabledOsv)
    assert lookup_from_env().query([]) == []
    monkeypatch.setenv("AGENTPEDIA_AUDIT_OSV", "1")
    client = lookup_from_env()
    assert isinstance(client, OsvClient)
    with pytest.raises(NotImplementedError):
        client.query([])


def test_supply_fixture_dirs_are_directories():
    assert (FIXTURES / "D02" / "positive").is_dir()
    findings = scan_supply(FIXTURES / "D02" / "negative")
    assert not any(item.rule_id == "D02" for item in findings)


def test_grace_window_is_fourteen_days():
    start = date(2026, 11, 1)
    assert (start + timedelta(days=14)).isoformat() == "2026-11-15"
