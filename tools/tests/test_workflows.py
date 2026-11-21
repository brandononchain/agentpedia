"""The workflows that execute repository code do not hold a write token."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"


def _text(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def test_certify_cannot_write_the_repository():
    text = _text("certify.yml")
    assert "pull_request_target" not in text
    assert "contents: write" not in text
    assert "contents: read" in text
    assert "pull-requests: write" not in text
    assert "git push" not in text
    assert "gh pr comment" not in text


def test_catalog_ci_is_read_only():
    text = _text("ci.yml")
    assert "pull_request_target" not in text
    assert "contents: write" not in text
    assert "contents: read" in text


def test_publish_workflow_does_not_execute_pull_request_code():
    text = _text("certify-publish.yml")
    assert "pull_request_target" not in text
    assert "actions/checkout" not in text
    assert "python3 tools/" not in text
    assert "contents: write" not in text
    assert "pull-requests: write" in text
    assert "workflow_run" in text


def test_audit_workflow_is_read_only():
    text = _text("audit.yml")
    assert "pull_request_target" not in text
    assert "contents: write" not in text
    assert "contents: read" in text
    assert "git push" not in text
    assert "--strict" in text
    assert "--ci" in text


def test_source_candidates_does_not_run_untrusted_pr_code():
    text = _text("source-candidates.yml")
    assert "pull_request:" not in text
    assert "pull_request_target" not in text
    assert "workflow_dispatch" in text
    assert "cron:" in text
    assert "ref: main" in text
    assert "git push origin candidates" in text
    assert "git push origin main" not in text
    assert "Refresh candidate queue" in text
    assert "contents: write" in text
    assert "contents: read" in text


def test_record_workflow_is_not_a_pull_request_job():
    text = _text("certify-record.yml")
    assert "pull_request:" not in text
    assert "pull_request_target" not in text
    assert "github.event.repository.default_branch" in text
    assert "contents: write" in text
