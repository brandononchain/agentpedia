import json
from pathlib import Path

from skill_lint.shelf_case import findings_for_category, findings_for_subshelf, shelf_label_error

GOOD = [
    "Agent Ops & Evals",
    "Data & Analysis",
    "DevOps & Cloud",
    "Security & Compliance",
    "Sales & GTM",
    "Marketing & X",
    "Design & Frontend",
    "Crypto & Onchain",
    "Rules of the Road",
]


def test_published_style_labels_pass():
    for label in GOOD:
        assert shelf_label_error(label) is None, label


def test_sentence_case_and_bad_acronyms_fail():
    assert shelf_label_error("Agent ops & evals") is not None
    assert shelf_label_error("Sales & gtm") is not None
    assert shelf_label_error("Marketing & x") is not None
    assert shelf_label_error("devops & Cloud") is not None
    assert shelf_label_error("  Data & Analysis") is not None


def test_category_file_finding(tmp_path: Path):
    meta = tmp_path / "category.json"
    meta.write_text('{"label": "Dev tools", "blurb": "Tools."}\n', encoding="utf-8")
    findings = findings_for_category(meta)
    assert any(item.rule_id == "shelf.label" for item in findings)
    assert all(item.severity == "error" for item in findings)

    meta.write_text(
        json.dumps(
            {
                "label": "Dev Tools",
                "blurb": "Tools.",
                "subshelves": [
                    {"slug": "git", "label": "Git", "description": "Commit messages from the branch."}
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    assert findings_for_category(meta) == []


def test_skill_subshelf_must_exist(tmp_path: Path):
    shelf = tmp_path / "trading"
    skill = shelf / "event-risk-guard"
    skill.mkdir(parents=True)
    (shelf / "category.json").write_text(
        json.dumps(
            {
                "label": "Trading & Markets",
                "blurb": "Plans and journals.",
                "subshelves": [
                    {"slug": "risk", "label": "Risk", "description": "Size and blackouts."}
                ],
            }
        ),
        encoding="utf-8",
    )
    skill_file = skill / "SKILL.md"
    skill_file.write_text("---\nname: event-risk-guard\n---\n", encoding="utf-8")
    missing = findings_for_subshelf(skill_file, {"metadata": {}})
    assert missing and missing[0].rule_id == "shelf.subshelf"
    unknown = findings_for_subshelf(skill_file, {"metadata": {"subshelf": "execution"}})
    assert unknown and "not on this shelf" in unknown[0].message
    assert findings_for_subshelf(skill_file, {"metadata": {"subshelf": "risk"}}) == []
