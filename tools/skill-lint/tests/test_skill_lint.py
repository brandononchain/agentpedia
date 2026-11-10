from __future__ import annotations

import json
from pathlib import Path

import pytest

from skill_lint.cli import lint_path, main
from skill_lint.discover import discover
from skill_lint.rules import lint_skill

FIXTURES = Path(__file__).resolve().parent / "fixtures"


def rule_ids(report) -> set[str]:
    return {finding.rule_id for finding in report.findings}


def test_good_skill_has_no_errors_or_warnings():
    report = lint_skill(FIXTURES / "good-pdf" / "SKILL.md")
    assert report.name == "good-pdf"
    problems = [f for f in report.findings if f.severity in {"error", "warn"}]
    assert problems == []


def test_missing_required_fields():
    report = lint_skill(FIXTURES / "missing-fields" / "SKILL.md")
    assert "spec.name.missing" in rule_ids(report)
    assert "spec.description.missing" in rule_ids(report)
    assert report.error_count >= 2


def test_invalid_name_xml_and_vague_description():
    report = lint_skill(FIXTURES / "Bad_Folder" / "SKILL.md")
    ids = rule_ids(report)
    assert "spec.name.invalid" in ids
    assert "spec.name.directory-mismatch" in ids
    assert "smell.name.unclear" in ids
    assert "smell.description.xml" in ids
    assert "smell.description.no-when" in ids
    assert "smell.description.vague" in ids


def test_description_length_limit():
    report = lint_skill(FIXTURES / "long-description" / "SKILL.md")
    assert "spec.description.too-long" in rule_ids(report)


def test_security_links_and_risky_shell():
    report = lint_skill(FIXTURES / "risky-skill" / "SKILL.md")
    ids = rule_ids(report)
    assert "security.curl-pipe-sh" in ids
    assert "security.rm-rf" in ids
    assert "security.secret" in ids
    assert "security.exfil-url" in ids
    assert "security.absolute-path" in ids
    assert "link.relative.missing" in ids
    assert "link.path.backslash" in ids
    assert any(f.severity == "error" and f.rule_id == "security.rm-rf" for f in report.findings)


def test_verbose_body_smells():
    report = lint_skill(FIXTURES / "verbose-skill" / "SKILL.md")
    ids = rule_ids(report)
    assert "smell.body.huge-inline-blob" in ids
    assert "smell.example.missing" in ids
    assert "smell.workflow.stepless" in ids
    assert "smell.validation.missing" in ids


def test_wrong_filename_case():
    report = lint_skill(FIXTURES / "wrong-case" / "skill.md")
    assert "spec.filename.case" in rule_ids(report)


def test_discover_folder_of_skills():
    found = discover(FIXTURES)
    names = sorted(path.name for path in found)
    assert "SKILL.md" in names
    assert "skill.md" in names
    assert len(found) >= 6


def test_cli_json_and_exit_codes(capsys):
    good = main(["--json", str(FIXTURES / "good-pdf")])
    payload = json.loads(capsys.readouterr().out)
    assert good == 0
    assert payload["summary"]["errors"] == 0
    assert payload["summary"]["skills"] == 1

    bad = main([str(FIXTURES / "missing-fields")])
    assert bad == 1
    text = capsys.readouterr().out
    assert "spec.name.missing" in text
    assert "fix:" in text


def test_missing_path_is_error(tmp_path):
    result = lint_path(tmp_path / "nope")
    assert result.error_count == 1
    assert result.extra_findings[0].rule_id == "scan.path.missing"


def test_empty_directory_is_error(tmp_path):
    result = lint_path(tmp_path)
    assert result.error_count == 1
    assert result.extra_findings[0].rule_id == "scan.skill.not-found"

def test_description_use_in_counts_as_when(tmp_path):
    skill_dir = tmp_path / "welcome-owner"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: welcome-owner\n"
        "description: >-\n"
        "  Use in the first conversation with a new owner to connect GrokChan,\n"
        "  register the bot, and get it claimed.\n"
        "---\n\n"
        "1. Ask for a display name.\n"
        "2. Connect the connector.\n"
        "3. Validate the claim link.\n\n"
        "Example: a new owner starts a chat and the bot walks through setup.\n",
        encoding="utf-8",
    )
    report = lint_skill(skill_dir / "SKILL.md")
    assert "smell.description.no-when" not in rule_ids(report)
    assert report.error_count == 0
