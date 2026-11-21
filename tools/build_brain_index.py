#!/usr/bin/env python3
"""Build data/brain-index.json for the Agentpedia Brain.

Reads data/catalog.json (and the certificate set for tier and status).
Writes one record per skill and agent that the static audit will serve:
on-hold, revoked, withheld, and grade F are left out. BM25 postings are
tokenized here so the API does not re-read every SKILL.md to score a query.

The file is generated. Rebuild it with this script. Do not hand-edit it.
"""

from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "skill-lint"))
sys.path.insert(0, str(ROOT / "tools"))

from brain_text import servable, tokenize  # noqa: E402
from skill_lint.frontmatter import split_frontmatter  # noqa: E402

CATALOG_PATH = ROOT / "data" / "catalog.json"
CERTS_PATH = ROOT / "data" / "certificates.json"
OUT_PATH = ROOT / "data" / "brain-index.json"

FIELDS = ("name", "title", "description", "tags", "shelf", "body")
TEXT_SUFFIXES = {".md", ".txt", ".py", ".js", ".mjs", ".yml", ".yaml", ".json", ".csv", ".toml"}
BODY_CAP = 50_000


def git_sha() -> str:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return "unknown"
    if completed.returncode != 0:
        return "unknown"
    return completed.stdout.strip() or "unknown"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def certificates_by_subject(catalog: dict) -> dict[tuple[str, str], dict]:
    found: dict[tuple[str, str], dict] = {}
    for document in catalog.get("certificates") or []:
        subject = (document.get("payload") or {}).get("subject") or {}
        kind = subject.get("kind")
        name = subject.get("name")
        if kind and name:
            found[(str(kind), str(name))] = document
    return found


def frontmatter_of(text: str) -> dict:
    parsed = split_frontmatter(text)
    fields = parsed.fields if parsed.present and not parsed.parse_error else {}
    return fields if isinstance(fields, dict) else {}


def read_body(directory: Path) -> str:
    if not directory.is_dir():
        return ""
    chunks: list[str] = []
    remaining = BODY_CAP
    files = sorted(
        (path for path in directory.rglob("*") if path.is_file()),
        key=lambda item: item.relative_to(directory).as_posix(),
    )
    for path in files:
        if remaining <= 0:
            break
        if any(part in {"__pycache__", ".git"} for part in path.parts) or path.suffix == ".pyc":
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"SKILL.md", "AGENT.md"}:
            continue
        data = path.read_bytes()
        if b"\0" in data:
            continue
        text = data.decode("utf-8", errors="replace")
        chunks.append(text[:remaining])
        remaining -= len(chunks[-1])
    return "\n".join(chunks)


def file_list(directory: Path) -> list[dict]:
    if not directory.is_dir():
        return []
    files = []
    for path in sorted(directory.rglob("*"), key=lambda item: item.relative_to(directory).as_posix()):
        if not path.is_file():
            continue
        if any(part in {"__pycache__", ".git"} for part in path.parts) or path.suffix == ".pyc":
            continue
        files.append({"path": path.relative_to(directory).as_posix(), "bytes": path.stat().st_size})
    return files


def claimed_tier(document: dict | None) -> str:
    if not document:
        return "listed"
    payload = document.get("payload") or {}
    claimed = str(payload.get("claimedTier") or "listed")
    if claimed not in {"listed", "verified", "certified"}:
        return "listed"
    return claimed


def cert_status_of(document: dict | None) -> str:
    if not document:
        return "active"
    return str((document.get("payload") or {}).get("status") or "active")


def build_entry(kind: str, item: dict, document: dict | None) -> dict | None:
    audit = item.get("audit") or {}
    digest = str(audit.get("contentDigest") or "")
    if not digest:
        payload = (document or {}).get("payload") or {}
        digest = str(payload.get("currentDigest") or payload.get("contentDigest") or "")
    status = cert_status_of(document)
    if not servable(audit, status, digest):
        return None
    source = Path(item["sourcePath"])
    directory = ROOT / source
    primary = directory / ("SKILL.md" if kind == "skill" else "AGENT.md")
    primary_text = primary.read_text(encoding="utf-8") if primary.is_file() else ""
    title = item.get("title") or item.get("name") or ""
    description = item.get("description") or ""
    tags = item.get("tags") or []
    if kind == "agent":
        tags = list(item.get("skills") or [])
    shelf_text = " ".join(
        [
            str(item.get("category") or ""),
            str(item.get("categoryLabel") or ""),
            str(item.get("subshelf") or ""),
            str(item.get("subshelfLabel") or ""),
            str(item.get("callNumber") or ""),
        ]
    )
    lint_score = 100
    if kind == "skill":
        lint_score = int((item.get("lint") or {}).get("score") or 0)
    elif document:
        lint_score = int(((document.get("payload") or {}).get("lint") or {}).get("score") or 100)
    field_tokens = {
        "name": tokenize(str(item.get("name") or "")),
        "title": tokenize(str(title)),
        "description": tokenize(str(description)),
        "tags": tokenize(" ".join(str(tag) for tag in tags)),
        "shelf": tokenize(shelf_text),
        "body": tokenize(read_body(directory)),
    }
    payload = (document or {}).get("payload") or {}
    return {
        "name": item["name"],
        "kind": kind,
        "title": title,
        "description": description,
        "tags": [str(tag) for tag in tags],
        "shelf": item.get("category") or "",
        "shelfLabel": item.get("categoryLabel") or "",
        "subShelf": item.get("subshelf") or "",
        "subShelfLabel": item.get("subshelfLabel") or "",
        "callNumber": item.get("callNumber") or "",
        "claimedTier": claimed_tier(document),
        "grade": audit.get("grade"),
        "auditScore": int(audit.get("score") or 0),
        "lintScore": lint_score,
        "digest": digest,
        "lockHash": audit.get("lockHash") or "",
        "lockHashAlg": audit.get("lockHashAlg") or "skills-lock-v2",
        "status": audit.get("status"),
        "certStatus": status,
        "expiresAt": audit.get("expiresAt") or "",
        "certExpiresAt": payload.get("expiresAt") or "",
        "auditedCommit": audit.get("auditedCommit") or "",
        "sourcePath": item.get("sourcePath") or "",
        "url": f"/{'skills' if kind == 'skill' else 'agents'}/{item['name']}",
        "frontmatter": frontmatter_of(primary_text),
        "files": file_list(directory),
        "fieldLength": {name: len(tokens) for name, tokens in field_tokens.items()},
        "_tokens": field_tokens,
    }


def build() -> dict:
    catalog = load_json(CATALOG_PATH)
    certificates = load_json(CERTS_PATH) if CERTS_PATH.is_file() else {"certificates": []}
    by_subject = certificates_by_subject(certificates)
    entries: list[dict] = []
    for kind, key in (("skill", "skills"), ("agent", "agents")):
        for item in catalog.get(key) or []:
            document = by_subject.get((kind, item.get("name")))
            built = build_entry(kind, item, document)
            if built:
                entries.append(built)
    entries.sort(key=lambda item: (item["kind"], item["name"]))

    postings: dict[str, list[list[int]]] = {}
    totals = Counter()
    for index, entry in enumerate(entries):
        tokens = entry.pop("_tokens")
        for field_index, field in enumerate(FIELDS):
            counts = Counter(tokens[field])
            totals[field] += len(tokens[field])
            for term, count in counts.items():
                rows = postings.setdefault(term, [])
                found = None
                for row in rows:
                    if row[0] == index:
                        found = row
                        break
                if found is None:
                    found = [index, 0, 0, 0, 0, 0, 0]
                    rows.append(found)
                found[field_index + 1] = count
    for rows in postings.values():
        rows.sort(key=lambda row: row[0])

    count = len(entries) or 1
    avg = {field: totals[field] / count for field in FIELDS}
    shelves = []
    served_shelves = {entry["shelf"] for entry in entries}
    for category in catalog.get("categories") or []:
        if category.get("id") not in served_shelves:
            continue
        shelves.append(
            {
                "id": category.get("id"),
                "label": category.get("label"),
                "number": category.get("number"),
                "blurb": category.get("blurb") or "",
                "subshelves": [
                    {
                        "slug": subshelf.get("slug"),
                        "label": subshelf.get("label"),
                        "description": subshelf.get("description") or "",
                        "number": subshelf.get("number"),
                    }
                    for subshelf in category.get("subshelves") or []
                ],
            }
        )
    return {
        "schema": "agentpedia.brain-index.v1",
        "version": git_sha(),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "tokenizer": "brain-v1",
        "bm25": {"k1": 1.2, "b": 0.75},
        "fieldWeights": {"name": 3, "title": 3, "description": 2, "tags": 2, "shelf": 1.5, "body": 1},
        "fields": list(FIELDS),
        "avgFieldLength": avg,
        "docCount": len(entries),
        "entries": entries,
        "postings": postings,
        "shelves": shelves,
    }


def main() -> None:
    if not CATALOG_PATH.is_file():
        raise SystemExit("data/catalog.json is missing. Run tools/build_index.py first.")
    index = build()
    OUT_PATH.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT_PATH.relative_to(ROOT)} ({index['docCount']} entries, version {index['version']})")


if __name__ == "__main__":
    main()
