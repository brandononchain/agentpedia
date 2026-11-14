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
    findings: list[Finding] = []
    reason = shelf_label_error(label)
    if reason is not None:
        findings.append(
            Finding(
                rule_id="shelf.label",
                severity="error",
                message=f"shelf label {label!r} is not title case: {reason}",
                hint="Example: 'Agent Ops & Evals', 'DevOps & Cloud', 'Sales & GTM'. The slug stays lowercase.",
                path=path,
            )
        )
    subs = data.get("subshelves")
    if not isinstance(subs, list) or not subs:
        findings.append(
            Finding(
                rule_id="shelf.subshelf",
                severity="error",
                message="category.json needs a subshelves list",
                hint="Each sub-shelf has slug, a title-cased label, and a one-line description.",
                path=path,
            )
        )
        return findings
    seen: set[str] = set()
    for index, item in enumerate(subs, start=1):
        if not isinstance(item, dict):
            findings.append(
                Finding(
                    rule_id="shelf.subshelf",
                    severity="error",
                    message=f"subshelf {index} must be an object",
                    hint="Use slug, label, and description.",
                    path=path,
                )
            )
            continue
        slug = str(item.get("slug") or "").strip()
        sub_label = item.get("label")
        if not slug or slug in seen or not isinstance(sub_label, str) or not str(item.get("description") or "").strip():
            findings.append(
                Finding(
                    rule_id="shelf.subshelf",
                    severity="error",
                    message=f"subshelf {index} needs a unique slug, a label, and a description",
                    hint="Keep the slug lowercase and the label in title case.",
                    path=path,
                )
            )
            continue
        seen.add(slug)
        sub_reason = shelf_label_error(sub_label)
        if sub_reason:
            findings.append(
                Finding(
                    rule_id="shelf.subshelf",
                    severity="error",
                    message=f"sub-shelf label {sub_label!r} is not title case: {sub_reason}",
                    hint="Example: 'Risk', 'Agent Ops'. The slug stays lowercase.",
                    path=path,
                )
            )
    return findings


def subshelf_error(fields: dict, category_dir: Path) -> str | None:
    """Return a reason when the entry's subshelf is missing or not on its shelf."""
    metadata = fields.get("metadata")
    if isinstance(metadata, dict) and str(metadata.get("subshelf") or "").strip():
        subshelf = str(metadata.get("subshelf")).strip()
    else:
        subshelf = str(fields.get("subshelf") or "").strip()
    meta_path = category_dir / "category.json"
    if not meta_path.is_file():
        return None
    if not subshelf:
        return "metadata.subshelf is required"
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    allowed = [
        str(item.get("slug"))
        for item in (data.get("subshelves") or [])
        if isinstance(item, dict) and item.get("slug")
    ]
    if subshelf not in allowed:
        listed = ", ".join(allowed) if allowed else "(none declared)"
        return f"metadata.subshelf {subshelf} is not on this shelf: {listed}"
    return None


def findings_for_subshelf(skill_file: Path, fields: dict) -> list[Finding]:
    reason = subshelf_error(fields, skill_file.parent.parent)
    if not reason:
        return []
    return [
        Finding(
            rule_id="shelf.subshelf",
            severity="error",
            message=reason,
            hint="Set metadata.subshelf to a slug listed in the shelf's category.json.",
            path=str(skill_file),
            line=1,
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
