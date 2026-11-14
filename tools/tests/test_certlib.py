"""Certificate evaluation, badges, and the check harness."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from certlib import (  # noqa: E402
    CertError,
    canonical,
    content_digest,
    evaluate_entry,
    manifest_digest,
)
from verify_checks import execute, validate_argv  # noqa: E402

COMMIT = "a" * 40
DIGEST = "sha256:" + "ab" * 32
OTHER = "sha256:" + "cd" * 32
HARNESS = "sha256:" + "ef" * 32
TODAY = date(2026, 11, 10)


def entry(digest: str = DIGEST, score: int = 100) -> dict:
    return {
        "kind": "skill",
        "name": "csv-profile",
        "title": "CSV profile",
        "source_path": "skills/data-analysis/csv-profile",
        "commit": COMMIT,
        "digest": digest,
        "lint": {
            "score": score,
            "errors": 0 if score == 100 else 1,
            "warnings": 0,
            "info": 0,
            "gate": "skill-lint",
            "summary": "skill-lint score. Listed requires 100.",
        },
    }


def record(tier: str = "listed", digest: str = DIGEST, issued: str = "2026-11-10", review=None) -> dict:
    return {
        "schema": "agentpedia.certificate-record.v1",
        "id": "skill-csv-profile",
        "subject": {"kind": "skill", "name": "csv-profile"},
        "tier": tier,
        "sourceCommit": COMMIT,
        "contentDigest": digest,
        "issuedAt": issued,
        "review": review,
    }


def run(digest: str = DIGEST, ran: str = "2026-11-10T12:00:00+00:00", ok: bool = True) -> dict:
    return {
        "schema": "agentpedia.check-result.v1",
        "id": "skill-csv-profile",
        "producer": "agentpedia-verify-checks",
        "ok": ok,
        "ranAt": ran,
        "sourceCommit": COMMIT,
        "contentDigest": digest,
        "harnessDigest": HARNESS,
        "manifestDigest": DIGEST,
        "checks": [
            {"id": "install-copy", "kind": "install", "ok": ok, "exitCode": 0, "durationMs": 3, "stdout": "files=2\n", "stderr": ""},
            {"id": "profile-sample", "kind": "eval", "ok": ok, "exitCode": 0, "durationMs": 8, "stdout": "rows=3\n", "stderr": ""},
        ],
    }


@pytest.fixture
def pinned_manifest(monkeypatch):
    monkeypatch.setattr("certlib.manifest_digest", lambda _identifier: DIGEST)


def payload(record_data, entry_data=None, result=None, today=TODAY):
    evaluated = evaluate_entry(entry_data or entry(), record_data, today, HARNESS, result=result)
    return evaluated["payload"], evaluated["svg"]


def test_canonical_is_sorted_and_matches_node():
    value = {"b": 1, "a": {"d": True, "c": ["x", None]}}
    text = canonical(value)
    assert text == '{"a":{"c":["x",null],"d":true},"b":1}'
    script = (
        "import { canonical } from './tools/cert_sign.mjs';"
        "process.stdout.write(canonical(JSON.parse(process.argv[1])));"
    )
    completed = subprocess.run(
        ["node", "--input-type=module", "--eval", script, json.dumps(value)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert completed.stdout == text


def test_content_digest_changes_when_a_file_changes(tmp_path: Path):
    folder = tmp_path / "entry"
    folder.mkdir()
    (folder / "SKILL.md").write_text("one\n", encoding="utf-8")
    first = content_digest(folder)
    (folder / "SKILL.md").write_text("two\n", encoding="utf-8")
    assert content_digest(folder) != first


def test_content_digest_ignores_catalog_placement(tmp_path: Path):
    folder = tmp_path / "entry"
    folder.mkdir()
    skill = """---
name: example
metadata:
  category: trading
  subshelf: risk
  tags: calendar
---

# Example

Do the work.
"""
    (folder / "SKILL.md").write_text(skill, encoding="utf-8")
    (folder / "notes.py").write_text("print(1)\n", encoding="utf-8")
    first = content_digest(folder)
    moved = skill.replace("category: trading", "category: legal-contracts").replace("subshelf: risk", "subshelf: execution")
    (folder / "SKILL.md").write_text(moved, encoding="utf-8")
    assert content_digest(folder) == first
    (folder / "SKILL.md").write_text(moved.replace("Do the work.", "Do other work."), encoding="utf-8")
    assert content_digest(folder) != first
    (folder / "SKILL.md").write_text(moved, encoding="utf-8")
    assert content_digest(folder) == first
    (folder / "notes.py").write_text("print(2)\n", encoding="utf-8")
    assert content_digest(folder) != first


def test_content_digest_keeps_subshelf_mentions_in_the_body(tmp_path: Path):
    folder = tmp_path / "agent"
    folder.mkdir()
    manifest = """---
name: trade-desk
category: trading
subshelf: risk
---

# Trade desk

The subshelf is part of this sentence.
"""
    (folder / "AGENT.md").write_text(manifest, encoding="utf-8")
    first = content_digest(folder)
    (folder / "AGENT.md").write_text(manifest.replace("category: trading", "category: product"), encoding="utf-8")
    assert content_digest(folder) == first
    (folder / "AGENT.md").write_text(
        manifest.replace("The subshelf is part of this sentence.", "The shelf label is not the work."),
        encoding="utf-8",
    )
    assert content_digest(folder) != first


def test_listed_is_active(pinned_manifest):
    body, svg = payload(record())
    assert body["status"] == "active"
    assert body["displayTier"] == "listed"
    assert body["expiresAt"] == "2027-11-10"
    assert body["urls"]["page"] == "https://agentpedia.sh/cert/skill-csv-profile"
    assert body["urls"]["badge"] == "https://agentpedia.sh/badge/skill-csv-profile.svg"
    assert body["urls"]["record"] == "https://agentpedia.sh/cert/skill-csv-profile.json"
    assert body["urls"]["publicKey"] == "https://agentpedia.sh/.well-known/agentpedia-signing-key.json"
    assert 'fill="#0e4f57"' in svg
    assert "rx=" not in svg


def test_source_change_is_recheck_pending(pinned_manifest):
    body, svg = payload(record(), entry(OTHER))
    assert body["status"] == "recheck-pending"
    assert body["displayTier"] == "recheck-pending"
    assert "re-check pending" in svg


def test_listed_expires_after_365_days(pinned_manifest):
    body, _svg = payload(record(issued="2025-11-09"), today=TODAY)
    assert body["status"] == "expired"


def test_score_below_100_is_withheld(pinned_manifest):
    body, _svg = payload(record(), entry(score=92))
    assert body["status"] == "withheld"


def test_verified_without_a_run_is_rejected(pinned_manifest):
    with pytest.raises(CertError, match="verify_checks"):
        payload(record("verified"), result=None)


def test_verified_run_is_active(pinned_manifest):
    body, svg = payload(record("verified"), result=run())
    assert body["status"] == "active"
    assert body["displayTier"] == "verified"
    assert body["run"]["countsAsVerification"] is True
    assert body["expiresAt"] == "2027-02-08"
    assert 'fill="#1d5c38"' in svg


def test_verified_run_expires_after_90_days(pinned_manifest):
    body, _svg = payload(record("verified"), result=run(ran="2026-08-01T00:00:00+00:00"))
    assert body["status"] == "expired"


def test_harness_change_is_recheck_pending(pinned_manifest):
    body, _svg = payload(record("verified"), result=run(), today=TODAY)
    stale = run()
    stale["harnessDigest"] = OTHER
    body, _svg = payload(record("verified"), result=stale)
    assert body["status"] == "recheck-pending"
    assert "harness" in body["statusReason"]


def test_certified_requires_a_review(pinned_manifest):
    with pytest.raises(CertError, match="review"):
        payload(record("certified"), result=run())


def test_certified_with_review_is_active(pinned_manifest):
    reviewed = record(
        "certified",
        review={"reviewer": "brandononchain", "date": "2026-11-10", "notes": "Read the skill and the recorded run."},
    )
    body, svg = payload(reviewed, result=run())
    assert body["displayTier"] == "certified"
    assert body["review"]["reviewer"] == "brandononchain"
    assert 'fill="#f4efe4"' in svg


def test_manifest_digest_helper_is_used():
    assert manifest_digest("does-not-exist") is None


def test_committed_evals_still_print_the_recorded_stdout():
    results = sorted((ROOT / "certs" / "results").glob("*.json"))
    assert [path.name for path in results] == [
        "skill-csv-profile.json",
        "skill-position-risk-sizer.json",
    ]
    for path in results:
        result = json.loads(path.read_text(encoding="utf-8"))
        assert result["ok"] is True
        assert result["producer"] == "agentpedia-verify-checks"
        evals = [check for check in result["checks"] if check["kind"] == "eval"]
        assert evals
        for check in evals:
            completed = subprocess.run(
                check["argv"],
                cwd=ROOT / check["cwd"],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
            assert completed.returncode == check["exitCode"]
            assert completed.stdout == check["stdout"]


def test_harness_runs_a_real_command_and_rejects_escape(tmp_path: Path):
    entry_dir = tmp_path / "demo-skill"
    script_dir = entry_dir / "scripts"
    script_dir.mkdir(parents=True)
    (entry_dir / "SKILL.md").write_text("# Demo\n", encoding="utf-8")
    (script_dir / "ok.py").write_text("print('rows=3')\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "-c", "user.email=test@example.com", "-c", "user.name=Test", "commit", "-m", "demo"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    manifest_path = tmp_path / "certs" / "checks" / "skill-demo-skill.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text(
        json.dumps(
            {
                "schema": "agentpedia.check-manifest.v1",
                "id": "skill-demo-skill",
                "entry": "demo-skill",
                "install": {"id": "install-copy", "kind": "copy-tree"},
                "evals": [
                    {
                        "id": "print-rows",
                        "argv": ["python3", "scripts/ok.py"],
                        "expectExit": 0,
                        "expectStdoutContains": ["rows=3"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    result = execute(tmp_path, manifest_path)
    assert result["ok"] is True
    assert result["checks"][1]["stdout"] == "rows=3\n"
    with pytest.raises(ValueError, match="escapes"):
        validate_argv(["python3", "../secret"], entry_dir)
