"""Queue trimming, license gates, and author credit. No network."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from sourcing.adapt import copyright_holder, resolve_author  # noqa: E402
from sourcing.candidate_queue import (  # noqa: E402
    build_document,
    license_decision,
    select_next,
)


def _raw(name: str, score: float, shelf: str, state: str = "compatible", repo: str = "github/example") -> dict:
    return {
        "name": name,
        "source_url": f"https://github.com/{repo}/blob/main/skills/{name}/SKILL.md",
        "repo": repo,
        "skill_path": f"skills/{name}/SKILL.md",
        "license": "mit",
        "license_status": state,
        "guessed_shelf": shelf,
        "rank_score": score,
        "already_in_catalog": False,
    }


def test_license_allow_and_copyleft():
    assert license_decision("MIT", "", "compatible") == ("MIT", "")
    assert license_decision("Apache-2.0", "", "compatible")[0] == "Apache-2.0"
    label, reason = license_decision("GPL-3.0", "", "compatible")
    assert label is None
    assert "cannot be imported" in reason
    label, reason = license_decision("", "", "readme-only")
    assert label is None
    assert "LICENSE file" in reason
    label, reason = license_decision("", "MIT License\n\nPermission is hereby granted, free of charge", "readme-only")
    assert label == "MIT"
    assert reason == ""
    label, reason = license_decision("", "GNU AFFERO GENERAL PUBLIC LICENSE", "readme-only")
    assert label is None


def test_trim_note_when_the_queue_is_large():
    rows = [_raw(f"skill-{index}", 1000 - index, "dev-tools") for index in range(40)]
    document = build_document(rows, set(), "2026-11-21T00:00:00+00:00", discovered=6693, max_bytes=800)
    assert document["counts"]["rows"] == 40 or "top 1500" in document["note"]
    assert "top 1500" in document["note"]
    assert document["counts"]["rows"] <= 1500
    assert document["candidates"][0]["score"] >= document["candidates"][-1]["score"]


def test_prefer_empty_shelves_orders_education_product_and_people_first():
    rows = [
        {
            "name": "commit-writer",
            "sourceUrl": "https://example.test/a",
            "repo": "github/example",
            "path": "skills/commit-writer/SKILL.md",
            "license": "MIT",
            "licenseState": "compatible",
            "shelf": "dev-tools",
            "score": 500,
            "status": "queued",
            "reason": "",
        },
        {
            "name": "lesson-plan",
            "sourceUrl": "https://example.test/b",
            "repo": "some-org/skills",
            "path": "skills/lesson-plan/SKILL.md",
            "license": "MIT",
            "licenseState": "compatible",
            "shelf": "education",
            "score": 10,
            "status": "queued",
            "reason": "",
        },
        {
            "name": "prd",
            "sourceUrl": "https://example.test/c",
            "repo": "github/awesome-copilot",
            "path": "skills/prd/SKILL.md",
            "license": "MIT",
            "licenseState": "compatible",
            "shelf": "product",
            "score": 20,
            "status": "queued",
            "reason": "",
        },
    ]
    ordered = select_next(rows, {"dev-tools": 12, "education": 0, "product": 0}, prefer_empty=True)
    assert [row["name"] for row in ordered] == ["prd", "lesson-plan", "commit-writer"]


def test_author_uses_a_stated_name_and_falls_back_to_the_login():
    mit = "MIT License\n\nCopyright (c) 2025 Addy Osmani\n"
    assert copyright_holder(mit) == "Addy Osmani"
    name, url, kind = resolve_author("addyosmani", "User", "Addy Osmani", mit, "")
    assert name == "Addy Osmani"
    assert url == "https://github.com/addyosmani"
    assert kind == "person"
    name, url, kind = resolve_author("github", "Organization", "", "MIT License\n\nCopyright GitHub, Inc.\n", "")
    assert name == "GitHub, Inc."
    assert kind == "organization"
    assert url == "https://github.com/github"
    name, url, kind = resolve_author("octocat", "User", "", "", "")
    assert name == "octocat"
    assert url == "https://github.com/octocat"
    assert "Jane" not in name
    apache = (
        "Licensor shall mean the copyright owner or entity authorized by\n"
        "      copyright notice that is included in or attached to the work\n"
        "Copyright [yyyy] [name of copyright owner]\n"
    )
    assert copyright_holder(apache) == ""
    name, _, kind = resolve_author("anthropics", "Organization", "Anthropic", apache, "")
    assert name == "Anthropic"
    assert kind == "organization"


def test_status_is_kept_when_the_queue_is_rebuilt():
    raw = [_raw("prd", 10, "product")]
    previous = [
        {
            "name": "prd",
            "sourceUrl": raw[0]["source_url"],
            "repo": "github/example",
            "path": "skills/prd/SKILL.md",
            "license": "MIT",
            "licenseState": "compatible",
            "shelf": "product",
            "score": 10,
            "status": "rejected",
            "reason": "lint 84",
        }
    ]
    document = build_document(raw, set(), "2026-11-21T00:00:00+00:00", previous)
    assert document["candidates"][0]["status"] == "rejected"
    assert document["candidates"][0]["reason"] == "lint 84"
