"""Compact candidate queue written to data/candidates.json.

The sourcer and the importer share this file. It is generated. Do not hand-merge it.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# About 2 MB. A larger discovery result keeps only the top compatible rows.
MAX_QUEUE_BYTES = 2_000_000
TOP_COMPATIBLE = 1500

PREFERRED_SHELVES = ("education", "product", "people")

OFFICIAL_ORGS = {
    "anthropics",
    "vercel-labs",
    "google",
    "github",
    "obsidianmd",
    "cloudflare",
    "nvidia",
    "googleworkspace",
    "obra",
    "addyosmani",
    "agentskills",
}

# Licenses the importer may adapt into the catalog. The SPDX id on the right
# is what the entry records.
ACCEPT_LICENSES = {
    "mit": "MIT",
    "apache-2.0": "Apache-2.0",
    "apache-2": "Apache-2.0",
    "bsd-2-clause": "BSD-2-Clause",
    "bsd-3-clause": "BSD-3-Clause",
    "isc": "ISC",
    "cc-by-4.0": "CC-BY-4.0",
    "cc0-1.0": "CC0-1.0",
    "cc0": "CC0-1.0",
    "unlicense": "Unlicense",
}

# Never copy these into the Apache-2.0 catalog, even if a detector calls them compatible.
REJECT_LICENSES = {
    "gpl-2.0",
    "gpl-2.0-only",
    "gpl-2.0-or-later",
    "gpl-3.0",
    "gpl-3.0-only",
    "gpl-3.0-or-later",
    "agpl-3.0",
    "agpl-3.0-only",
    "agpl-3.0-or-later",
    "lgpl-2.1",
    "lgpl-2.1-only",
    "lgpl-3.0",
    "lgpl-3.0-only",
    "cc-by-sa-3.0",
    "cc-by-sa-4.0",
}

LICENSE_LABELS = {
    "mit": "MIT",
    "apache-2.0": "Apache-2.0",
    "bsd-2-clause": "BSD-2-Clause",
    "bsd-3-clause": "BSD-3-Clause",
    "bsd-3-clause-clear": "BSD-3-Clause-Clear",
    "isc": "ISC",
    "0bsd": "0BSD",
    "unlicense": "Unlicense",
    "cc0-1.0": "CC0-1.0",
    "cc-by-4.0": "CC-BY-4.0",
    "cc-by-3.0": "CC-BY-3.0",
    "cc-by-sa-4.0": "CC-BY-SA-4.0",
    "gpl-2.0": "GPL-2.0",
    "gpl-3.0": "GPL-3.0",
    "agpl-3.0": "AGPL-3.0",
    "lgpl-2.1": "LGPL-2.1",
    "lgpl-3.0": "LGPL-3.0",
    "mpl-2.0": "MPL-2.0",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slug(value: str) -> str:
    text = value.strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return re.sub(r"-{2,}", "-", text).strip("-")


def license_key(raw: str | None) -> str:
    if not raw:
        return ""
    text = raw.strip().lower().replace("_", "-")
    text = text.replace(" ", "")
    if "apache" in text and "2" in text:
        return "apache-2.0"
    if text.startswith("mit"):
        return "mit"
    if "bsd-3" in text or "bsd3" in text or "3-clause" in text or "3clause" in text:
        return "bsd-3-clause"
    if "bsd-2" in text or "bsd2" in text or "2-clause" in text or "2clause" in text:
        return "bsd-2-clause"
    if text in {"isc"}:
        return "isc"
    if "cc0" in text or "cc-zero" in text:
        return "cc0-1.0"
    if "cc-by-sa" in text or "ccbysa" in text:
        return "cc-by-sa-4.0"
    if "cc-by" in text or "ccby" in text:
        return "cc-by-4.0"
    if "agpl" in text:
        return "agpl-3.0"
    if "lgpl" in text:
        return "lgpl-3.0"
    if "gpl-3" in text or "gplv3" in text or text in {"gpl3", "gpl-3.0"}:
        return "gpl-3.0"
    if "gpl-2" in text or "gplv2" in text or text in {"gpl2", "gpl-2.0"}:
        return "gpl-2.0"
    if "gpl" in text:
        return "gpl-3.0"
    if "unlicense" in text:
        return "unlicense"
    if text in {"unknown", "other", "noassertion", "none", ""}:
        return ""
    return text.strip("-")


def license_label(raw: str | None) -> str:
    key = license_key(raw)
    if not key:
        return "unknown"
    return LICENSE_LABELS.get(key, raw.strip() if raw else key)


def map_license_state(raw_state: str | None, raw_license: str | None = None) -> str:
    state = (raw_state or "").strip().lower().replace("-", "_")
    if state in {"compatible_unverified", "readme_only", "readme-only"}:
        return "readme-only"
    if state in {"compatible", "copyleft", "unknown", "readme-only"}:
        return "readme-only" if state == "readme-only" else state
    key = license_key(raw_license)
    if key in REJECT_LICENSES:
        return "copyleft"
    if key in ACCEPT_LICENSES:
        return "compatible"
    return "unknown"


def accept_license(raw: str | None) -> str | None:
    """Return the SPDX label when the license may be imported, else None."""
    key = license_key(raw)
    if not key or key in REJECT_LICENSES:
        return None
    return ACCEPT_LICENSES.get(key)


def detect_license_text(text: str) -> str:
    """SPDX key from a LICENSE file body. Empty when the text is not recognized."""
    if not text:
        return ""
    sample = text.lower()
    if "affero" in sample or "agpl" in sample:
        return "agpl-3.0"
    if "lesser general public" in sample or "lgpl" in sample:
        return "lgpl-3.0"
    if "general public license" in sample or re.search(r"\bgpl\b", sample):
        return "gpl-3.0"
    if "sharealike" in sample or "cc by-sa" in sample or "cc-by-sa" in sample:
        return "cc-by-sa-4.0"
    if "creative commons attribution" in sample or "cc by 4" in sample or "cc-by-4" in sample:
        return "cc-by-4.0"
    if "cc0" in sample or "public domain dedication" in sample:
        return "cc0-1.0"
    if "apache license" in sample and "2.0" in sample:
        return "apache-2.0"
    if "isc license" in sample or "permission to use, copy, modify, and/or distribute" in sample:
        return "isc"
    if "this is free and unencumbered software released into the public domain" in sample or "the unlicense" in sample:
        return "unlicense"
    if "mit license" in sample or (
        "permission is hereby granted, free of charge" in sample and "without restriction" in sample
    ):
        return "mit"
    if "redistribution and use" in sample and "bsd" in sample:
        return "bsd-3-clause" if "neither the name" in sample or sample.count("redistribution") >= 1 and "3." in sample else "bsd-2-clause"
    return ""


def license_decision(spdx: str, license_file: str, queue_state: str) -> tuple[str | None, str]:
    """Return (accepted SPDX label, reason). A missing label means do not import."""
    if is_rejected_family(spdx) or queue_state == "copyleft":
        label = license_label(spdx) if spdx else "copyleft"
        return None, f"license {label} cannot be imported (GPL, AGPL, LGPL, and CC-BY-SA stay out)"
    accepted = accept_license(spdx)
    if accepted and queue_state != "readme-only":
        return accepted, ""
    file_key = detect_license_text(license_file)
    if is_rejected_family(file_key):
        return None, f"LICENSE file is {license_label(file_key)} and cannot be imported"
    file_ok = accept_license(file_key)
    if queue_state == "readme-only" or not accepted:
        if not license_file.strip():
            return None, "readme-only license needs a LICENSE file"
        if file_ok:
            return file_ok, ""
        if accepted:
            return accepted, ""
        return None, "license is not in the allow list (MIT, Apache-2.0, BSD-2/3, ISC, CC-BY-4.0, CC0, Unlicense)"
    return accepted, ""


def is_rejected_family(raw: str | None) -> bool:
    return license_key(raw) in REJECT_LICENSES


def row_key(row: dict[str, Any]) -> str:
    repo = str(row.get("repo") or "").lower()
    path = str(row.get("path") or row.get("skill_path") or "").lower()
    url = str(row.get("sourceUrl") or row.get("source_url") or "")
    if repo and path:
        return f"{repo}::{path}"
    return url or f"{repo}::{slug(str(row.get('name') or ''))}"


def _field(row: dict[str, Any], *names: str, default: str = "") -> str:
    for name in names:
        value = row.get(name)
        if value is not None and str(value).strip() != "":
            return str(value).strip()
    return default


def compact_row(raw: dict[str, Any], catalog_names: set[str]) -> dict[str, Any] | None:
    """One queue row, or None when the row is not compatible or readme-only."""
    state = map_license_state(
        _field(raw, "licenseState", "license_status"),
        _field(raw, "license"),
    )
    if state not in {"compatible", "readme-only"}:
        return None
    name = slug(_field(raw, "name"))
    if not name:
        return None
    already = bool(raw.get("already_in_catalog")) or name in catalog_names
    if already:
        return None
    repo = _field(raw, "repo")
    if repo.lower().startswith("brandononchain/agentpedia"):
        return None
    path = _field(raw, "path", "skill_path")
    license_raw = _field(raw, "license")
    try:
        score = float(raw.get("score") if raw.get("score") is not None else raw.get("rank_score") or 0)
    except (TypeError, ValueError):
        score = 0.0
    status = _field(raw, "status", default="queued")
    if status not in {"queued", "imported", "rejected"}:
        status = "queued"
    return {
        "name": name,
        "sourceUrl": _field(raw, "sourceUrl", "source_url"),
        "repo": repo,
        "path": path,
        "license": license_label(license_raw) if license_raw and license_raw.lower() != "unknown" else license_label(state),
        "licenseState": state,
        "shelf": _field(raw, "shelf", "guessed_shelf") or "dev-tools",
        "score": round(score, 2),
        "status": status,
        "reason": _field(raw, "reason"),
    }


def _render(rows: list[dict[str, Any]], generated_at: str, note: str, discovered: int) -> dict[str, Any]:
    counts = {
        "rows": len(rows),
        "compatible": sum(1 for row in rows if row["licenseState"] == "compatible"),
        "readmeOnly": sum(1 for row in rows if row["licenseState"] == "readme-only"),
        "withPath": sum(1 for row in rows if str(row.get("path") or "").lower().endswith("skill.md")),
        "queued": sum(1 for row in rows if row["status"] == "queued"),
        "imported": sum(1 for row in rows if row["status"] == "imported"),
        "rejected": sum(1 for row in rows if row["status"] == "rejected"),
        "discovered": discovered,
    }
    return {
        "generatedAt": generated_at,
        "note": note,
        "counts": counts,
        "candidates": rows,
    }


def _encoded_size(document: dict[str, Any]) -> int:
    return len(json.dumps(document, indent=2).encode("utf-8")) + 1


def fit_queue(
    rows: list[dict[str, Any]],
    generated_at: str,
    discovered: int,
    compatible_total: int,
    readme_total: int,
    max_bytes: int = MAX_QUEUE_BYTES,
) -> dict[str, Any]:
    """Keep compatible and readme-only rows. Trim to the top compatible scores past 2 MB."""
    compatible = [row for row in rows if row["licenseState"] == "compatible"]
    readme = [row for row in rows if row["licenseState"] == "readme-only"]
    compatible.sort(key=lambda row: (-float(row["score"]), row["name"]))
    readme.sort(key=lambda row: (-float(row["score"]), row["name"]))
    pinned = [row for row in rows if row["status"] in {"imported", "rejected"}]
    chosen = _dedupe(compatible + readme)
    note = (
        f"Compatible and readme-only rows from a discovery of {discovered} candidates "
        f"({compatible_total} compatible, {readme_total} readme-only before catalog dedupe). "
        "Unknown and copyleft rows are omitted."
    )
    document = _render(chosen, generated_at, note, discovered)
    if _encoded_size(document) <= max_bytes:
        return document
    trimmed = _dedupe(compatible[:TOP_COMPATIBLE] + pinned)
    note = (
        f"Trimmed to the top {TOP_COMPATIBLE} compatible rows by score because the full queue "
        f"exceeded {max(1, max_bytes // 1_000_000)} MB. Discovery found {discovered} candidates, "
        f"{compatible_total} of them license-compatible"
        f"{f' and {readme_total} readme-only' if readme_total else ''}. "
        "Unknown, copyleft, and the lower-scored compatible rows are omitted. "
        "Imported and rejected rows are kept so a later run does not retry them."
    )
    return _render(trimmed, generated_at, note, discovered)


def _dedupe(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    kept: list[dict[str, Any]] = []
    for row in rows:
        key = row_key(row)
        if key in seen:
            continue
        seen.add(key)
        kept.append(row)
    return kept


def merge_status(rows: list[dict[str, Any]], previous: list[dict[str, Any]]) -> None:
    """Keep imported and rejected decisions when the sourcer runs again."""
    prior = {row_key(row): row for row in previous}
    for row in rows:
        old = prior.get(row_key(row))
        if not old:
            continue
        if old.get("status") in {"imported", "rejected"}:
            row["status"] = old["status"]
            row["reason"] = old.get("reason") or row.get("reason") or ""


def build_document(
    raw_rows: list[dict[str, Any]],
    catalog_names: set[str],
    generated_at: str,
    previous: list[dict[str, Any]] | None = None,
    discovered: int | None = None,
    max_bytes: int = MAX_QUEUE_BYTES,
) -> dict[str, Any]:
    discovered = discovered if discovered is not None else len(raw_rows)
    compatible_total = 0
    readme_total = 0
    compact: list[dict[str, Any]] = []
    for raw in raw_rows:
        state = map_license_state(
            str(raw.get("licenseState") or raw.get("license_status") or ""),
            str(raw.get("license") or ""),
        )
        if state == "compatible":
            compatible_total += 1
        elif state == "readme-only":
            readme_total += 1
        row = compact_row(raw, catalog_names)
        if row:
            compact.append(row)
    merge_status(compact, previous or [])
    return fit_queue(compact, generated_at, discovered, compatible_total, readme_total, max_bytes=max_bytes)


def load_queue(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"generatedAt": "", "note": "", "counts": {}, "candidates": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {"generatedAt": "", "note": "", "counts": {}, "candidates": data}
    data.setdefault("candidates", [])
    return data


def save_queue(path: Path, document: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = document.get("candidates") or []
    counts = {
        "rows": len(rows),
        "compatible": sum(1 for row in rows if row.get("licenseState") == "compatible"),
        "readmeOnly": sum(1 for row in rows if row.get("licenseState") == "readme-only"),
        "withPath": sum(1 for row in rows if str(row.get("path") or "").lower().endswith("skill.md")),
        "queued": sum(1 for row in rows if row.get("status") == "queued"),
        "imported": sum(1 for row in rows if row.get("status") == "imported"),
        "rejected": sum(1 for row in rows if row.get("status") == "rejected"),
        "discovered": (document.get("counts") or {}).get("discovered", len(rows)),
    }
    document["counts"] = counts
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def shelf_counts(skills_dir: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    if not skills_dir.is_dir():
        return counts
    for category in skills_dir.iterdir():
        if not category.is_dir() or not (category / "category.json").is_file():
            continue
        counts[category.name] = sum(1 for child in category.iterdir() if (child / "SKILL.md").is_file())
    return counts


def select_next(
    rows: list[dict[str, Any]],
    shelf_counts_map: dict[str, int],
    prefer_empty: bool,
) -> list[dict[str, Any]]:
    """Queued compatible rows that have a SKILL.md path, preferred shelves and orgs first."""

    def sort_key(row: dict[str, Any]) -> tuple:
        shelf = str(row.get("shelf") or "")
        if prefer_empty and shelf in PREFERRED_SHELVES:
            band = 0
        elif prefer_empty:
            band = 1 + shelf_counts_map.get(shelf, 50)
        else:
            band = 0
        org = str(row.get("repo") or "").split("/")[0].lower()
        official = 0 if org in OFFICIAL_ORGS else 1
        return (band, official, -float(row.get("score") or 0), row.get("name") or "")

    queued = []
    for row in rows:
        if row.get("status") != "queued":
            continue
        if row.get("licenseState") != "compatible":
            continue
        path = str(row.get("path") or "")
        if not path.lower().endswith("skill.md"):
            continue
        if not row.get("sourceUrl") and not row.get("repo"):
            continue
        queued.append(row)
    queued.sort(key=sort_key)
    return queued


def update_row(rows: list[dict[str, Any]], key: str, status: str, reason: str) -> None:
    for row in rows:
        if row_key(row) == key:
            row["status"] = status
            row["reason"] = reason
            return
