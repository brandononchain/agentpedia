"""Title case for shelf display names stored in category.json."""

from __future__ import annotations

import json
from pathlib import Path

from skill_lint.models import Finding

# Words that stay fully capitalized. X is the name of the network, not a letter grade.
ACRONYMS = frozenset(
    {
        "AI",
        "API",
        "AWS",
        "CI",
        "CSS",
        "CSV",
        "ETL",
        "GTM",
        "HTML",
        "MCP",
        "NDA",
        "PDF",
        "SQL",
        "UI",
        "UX",
        "X",
    }
)
# Interior capitals that title case would otherwise flatten.
SPECIAL = frozenset({"DevOps"})
MINOR = frozenset(
    {
        "a",
        "an",
        "and",
        "as",
        "at",
        "but",
        "by",
        "for",
        "from",
        "in",
        "nor",
        "of",
        "on",
        "or",
        "the",
        "to",
        "vs",
    }
)


def _title_word(word: str) -> bool:
    if not word or not word[0].isupper():
        return False
    rest = word[1:]
    if rest != rest.lower():
        return False
    return all(char.isalpha() or char == "'" for char in word)


def shelf_label_error(label: str) -> str | None:
    """Return a short reason the label is not a shelf display name, or None."""
    if not label or not label.strip():
        return "the label is empty"
    if label != " ".join(label.split(" ")):
        return "use single spaces, with no leading or trailing space"
    words = label.split(" ")
    last = len(words) - 1
    for index, word in enumerate(words):
        if word == "&":
            continue
        if word in ACRONYMS or word in SPECIAL:
            continue
        if "-" in word:
            parts = word.split("-")
            if parts and all(_title_word(part) for part in parts):
                continue
            return f"'{word}' is not title case"
        if word.lower() in MINOR and 0 < index < last:
            if word != word.lower():
                return f"'{word}' stays lowercase in the middle of a shelf name"
            continue
        if _title_word(word):
            continue
        return (
            f"'{word}' is not title case. Capitalize each main word, "
            "and keep acronyms in capitals (GTM, UI, ETL, MCP, X)."
        )
    return None


def findings_for_category(meta: Path) -> list[Finding]:
    path = str(meta)
    try:
        data = json.loads(meta.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [
            Finding(
                rule_id="shelf.label",
                severity="error",
                message=f"category.json is not valid JSON ({exc.msg})",
                hint="Keep label and blurb in category.json.",
                path=path,
            )
        ]
    if not isinstance(data, dict):
        return [
            Finding(
                rule_id="shelf.label",
                severity="error",
                message="category.json must be an object with label and blurb",
                hint="Store the shelf display name in label.",
                path=path,
            )
        ]
    label = data.get("label")
    if not isinstance(label, str):
        return [
            Finding(
                rule_id="shelf.label",
                severity="error",
                message="category.json needs a string label",
                hint="The label is the shelf name shown in the nav, cards, and metadata.",
                path=path,
            )
        ]
    reason = shelf_label_error(label)
    if reason is None:
        return []
    return [
        Finding(
            rule_id="shelf.label",
            severity="error",
            message=f"shelf label {label!r} is not title case: {reason}",
            hint="Example: 'Agent Ops & Evals', 'DevOps & Cloud', 'Sales & GTM'. The slug stays lowercase.",
            path=path,
        )
    ]


def category_files_for(skill_files: list[Path]) -> list[Path]:
    found: list[Path] = []
    seen: set[Path] = set()
    for skill in skill_files:
        meta = skill.parent.parent / "category.json"
        if meta in seen or not meta.is_file():
            continue
        seen.add(meta)
        found.append(meta)
    return found
