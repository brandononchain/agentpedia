from pathlib import Path

from skill_lint.shelf_case import findings_for_category, shelf_label_error

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
    assert len(findings) == 1
    assert findings[0].rule_id == "shelf.label"
    assert findings[0].severity == "error"

    meta.write_text('{"label": "Dev Tools", "blurb": "Tools."}\n', encoding="utf-8")
    assert findings_for_category(meta) == []
