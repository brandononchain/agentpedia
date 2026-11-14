#!/usr/bin/env python3
"""Certificate records for Agentpedia.

A record in certs/records/<id>.json is a claim: a tier, the source commit,
the digest of the entry directory, and an issue date. This module checks
that claim against the tree being built. It never invents a verification
run or a human review. Those exist only when their files exist.

Tiers
-----
listed
    skill-lint score is 100, or an agent whose bundled skills all score 100.
verified
    listed, plus certs/results/<id>.json produced by tools/verify_checks.py.
certified
    verified, plus a review object on the record (reviewer, date, notes).

Clocks
------
A changed entry digest sets status to recheck-pending.
The digest covers instructions and assets. It skips catalog placement:
category and subshelf in the entry frontmatter, and the shelf number,
sub-shelf order, and call number, which live in category.json outside
the entry directory. A shelf move does not by itself invalidate a certificate.
Listed lapses 365 days after issuedAt.
A verification run lapses 90 days after it ran.
A human review lapses 365 days after its date.
Certified stays current only while both the run and the review are current.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDS_DIR = ROOT / "certs" / "records"
RESULTS_DIR = ROOT / "certs" / "results"
CHECKS_DIR = ROOT / "certs" / "checks"
PUBLIC_KEY_PATH = ROOT / "certs" / "public-key.json"
DATA_PATH = ROOT / "data" / "certificates.json"
BADGE_DIR = ROOT / "public" / "badge"
CERT_PUBLIC_DIR = ROOT / "public" / "cert"
WELL_KNOWN_PATH = ROOT / "public" / ".well-known" / "agentpedia-signing-key.json"
HARNESS_PATH = ROOT / "tools" / "verify_checks.py"
SITE_CONFIG_PATH = ROOT / "config" / "site.json"

RECORD_SCHEMA = "agentpedia.certificate-record.v1"
SET_SCHEMA = "agentpedia.certificate-set.v1"
PAYLOAD_SCHEMA = "agentpedia.certificate.v1"
RESULT_SCHEMA = "agentpedia.check-result.v1"
KEY_SCHEMA = "agentpedia.signing-key.v1"

LISTED_DAYS = 365
VERIFIED_DAYS = 90
REVIEW_DAYS = 365

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LOGIN_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")
ID_RE = re.compile(r"^(skill|agent)-[a-z0-9]+(?:-[a-z0-9]+)*$")

LIMITS = [
    "This certificate is not a security audit.",
    "It does not claim the entry is safe against a hostile user or a hostile file.",
    "Listed means the published lint gate scored 100 on this exact tree.",
    "Verified means that gate plus the recorded install probe and evals exited cleanly in the check sandbox.",
    "Certified means Verified plus one named review stored in this repository.",
    "The check sandbox is a scrubbed subprocess with a timeout. It is not a virtual machine.",
]

SOURCE_RULE = (
    "The certificate names one git commit and one sha256 digest of the entry directory. "
    "The digest covers the instructions and assets. It skips catalog placement: "
    "category and subshelf in the frontmatter, and the shelf number, sub-shelf order, "
    "and call number stored in category.json outside the entry. "
    "A different digest sets the status to re-check pending."
)
EXPIRY_RULE = (
    "Listed stays current for 365 days after issuedAt. "
    "A verification run stays current for 90 days after ranAt. "
    "A human review stays current for 365 days after its date. "
    "Certified requires both the run and the review to be current."
)

LABEL_BG = "#1c1915"
LABEL_FG = "#f4efe4"
BADGE_COLORS = {
    "listed": ("#0e4f57", "#f4efe4"),
    "verified": ("#1d5c38", "#f4efe4"),
    "certified": ("#f4efe4", "#1c1915"),
    "recheck-pending": ("#6b4a12", "#f4efe4"),
    "expired": ("#8d1d1d", "#f4efe4"),
    "withheld": ("#534e45", "#f4efe4"),
}
BADGE_MESSAGE = {
    "listed": "listed",
    "verified": "verified",
    "certified": "certified",
    "recheck-pending": "re-check pending",
    "expired": "expired",
    "withheld": "not listed",
}

SKIP_DIRS = {"__pycache__", ".pytest_cache"}
# Placement in the catalog. These lines do not change what the entry tells an agent to do.
CATALOG_PLACEMENT_KEYS = frozenset({"category", "subshelf"})
_PLACEMENT_LINE = re.compile(r"^[ \t]*(category|subshelf)[ \t]*:")
_AUTO = object()


class CertError(Exception):
    """The claim cannot be published as made."""


def canonical(value: object) -> str:
    """UTF-8 JSON with sorted keys and no insignificant whitespace."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def site_origin() -> str:
    """Public origin. NEXT_PUBLIC_SITE_URL overrides config/site.json."""
    override = os.environ.get("NEXT_PUBLIC_SITE_URL", "").strip()
    if override:
        return override.rstrip("/")
    if not SITE_CONFIG_PATH.is_file():
        raise CertError("config/site.json is missing")
    config = json.loads(SITE_CONFIG_PATH.read_text(encoding="utf-8"))
    origin = str(config.get("origin") or "").strip().rstrip("/")
    if not origin:
        raise CertError("config/site.json is missing origin")
    return origin


def today_iso() -> str:
    override = os.environ.get("AGENTPEDIA_TODAY", "").strip()
    if override:
        if not DATE_RE.fullmatch(override):
            raise CertError("AGENTPEDIA_TODAY must be YYYY-MM-DD")
        return override
    return datetime.now(timezone.utc).date().isoformat()


def parse_date(value: str) -> date:
    if not DATE_RE.fullmatch(value):
        raise CertError(f"bad date {value!r}")
    year, month, day = (int(part) for part in value.split("-"))
    try:
        return date(year, month, day)
    except ValueError as exc:
        raise CertError(f"bad date {value}") from exc


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def digest_bytes(path: Path) -> bytes:
    """Bytes that enter the digest. Catalog placement lines are omitted from frontmatter."""
    data = path.read_bytes()
    if path.name not in {"SKILL.md", "AGENT.md"}:
        return data
    text = data.decode("utf-8")
    if not text.startswith("---"):
        return data
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return data
    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
    if end is None:
        return data
    kept = [lines[0]]
    for line in lines[1:end]:
        match = _PLACEMENT_LINE.match(line)
        if match and match.group(1) in CATALOG_PLACEMENT_KEYS:
            continue
        kept.append(line)
    kept.extend(lines[end:])
    return "".join(kept).encode("utf-8")


def content_digest(directory: Path) -> str:
    """Digest of the instructions and assets in a skill or agent directory.

    category.json is not inside that directory, so the shelf number, the
    sub-shelf order, and the call number are not part of the digest.
    category and subshelf lines in SKILL.md or AGENT.md frontmatter are
    removed before hashing. A change to steps, scripts, references, or any
    other file still changes the digest.
    """
    if not directory.is_dir():
        raise CertError(f"missing entry directory {directory}")
    hasher = hashlib.sha256()
    files = []
    for path in directory.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts) or path.suffix == ".pyc":
            continue
        files.append(path)
    for path in sorted(files, key=lambda item: item.relative_to(directory).as_posix()):
        rel = path.relative_to(directory).as_posix().encode()
        data = digest_bytes(path)
        hasher.update(rel)
        hasher.update(b"\0")
        hasher.update(str(len(data)).encode())
        hasher.update(b"\0")
        hasher.update(data)
        hasher.update(b"\0")
    return "sha256:" + hasher.hexdigest()


def git_commit(root: Path, directory: Path) -> str:
    """Last commit that touched this entry. Empty when git cannot answer."""
    try:
        relative = directory.relative_to(root).as_posix()
    except ValueError:
        relative = str(directory)
    try:
        completed = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", relative],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        return ""
    if completed.returncode != 0:
        return ""
    return completed.stdout.strip()


def cert_id(kind: str, name: str) -> str:
    return f"{kind}-{name}"


def entry_path(kind: str, name: str) -> str:
    return f"/skills/{name}" if kind == "skill" else f"/agents/{name}"


def dump_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CertError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise CertError(f"{path} must be a JSON object")
    return data


def load_records() -> dict[str, dict]:
    records: dict[str, dict] = {}
    if not RECORDS_DIR.is_dir():
        return records
    for path in sorted(RECORDS_DIR.glob("*.json")):
        record = load_json(path)
        validate_record_shape(record, path.name)
        if path.stem != record["id"]:
            raise CertError(f"{path.name} must be named {record['id']}.json")
        records[record["id"]] = record
    return records


def validate_record_shape(record: dict, label: str) -> None:
    if record.get("schema") != RECORD_SCHEMA:
        raise CertError(f"{label} schema must be {RECORD_SCHEMA}")
    identifier = record.get("id")
    subject = record.get("subject")
    if not isinstance(identifier, str) or not ID_RE.fullmatch(identifier):
        raise CertError(f"{label} has an invalid id")
    if not isinstance(subject, dict):
        raise CertError(f"{label} is missing subject")
    kind = subject.get("kind")
    name = subject.get("name")
    if kind not in {"skill", "agent"} or not isinstance(name, str) or not name:
        raise CertError(f"{label} subject must name a skill or an agent")
    if identifier != cert_id(kind, name):
        raise CertError(f"{label} id does not match its subject")
    if record.get("tier") not in {"listed", "verified", "certified"}:
        raise CertError(f"{label} tier must be listed, verified, or certified")
    if not isinstance(record.get("sourceCommit"), str) or not SHA_RE.fullmatch(record["sourceCommit"]):
        raise CertError(f"{label} sourceCommit must be a 40-character git sha")
    if not isinstance(record.get("contentDigest"), str) or not DIGEST_RE.fullmatch(record["contentDigest"]):
        raise CertError(f"{label} contentDigest must be sha256:<64 hex>")
    parse_date(str(record.get("issuedAt", "")))
    review = record.get("review")
    if review is not None and not isinstance(review, dict):
        raise CertError(f"{label} review must be an object or null")


def listed_record(entry: dict, digest: str, commit: str, issued_at: str) -> dict:
    if not SHA_RE.fullmatch(commit):
        raise CertError(
            f"{cert_id(entry['kind'], entry['name'])} has no committed source. "
            "Commit the entry, then rebuild so the certificate can name that commit."
        )
    return {
        "schema": RECORD_SCHEMA,
        "id": cert_id(entry["kind"], entry["name"]),
        "subject": {"kind": entry["kind"], "name": entry["name"]},
        "tier": "listed",
        "sourceCommit": commit,
        "contentDigest": digest,
        "issuedAt": issued_at,
        "review": None,
    }


def qualifies(entry: dict) -> bool:
    lint = entry["lint"]
    return lint["score"] == 100 and lint["errors"] == 0 and lint["warnings"] == 0


def ensure_listed_records(entries: list[dict], today: str) -> list[str]:
    """Write a Listed record for every qualifying entry that does not have one."""
    created: list[str] = []
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)
    existing = {path.stem for path in RECORDS_DIR.glob("*.json")}
    for entry in entries:
        identifier = cert_id(entry["kind"], entry["name"])
        if identifier in existing or not qualifies(entry):
            continue
        directory = ROOT / entry["source_path"]
        record = listed_record(entry, content_digest(directory), git_commit(ROOT, directory), today)
        dump_json(RECORDS_DIR / f"{identifier}.json", record)
        created.append(identifier)
    return created


def _past(start: str, days: int, today: date) -> bool:
    return today > parse_date(start) + timedelta(days=days)


def _expires(start: str, days: int) -> str:
    return (parse_date(start) + timedelta(days=days)).isoformat()


def load_result(identifier: str) -> dict | None:
    path = RESULTS_DIR / f"{identifier}.json"
    if not path.is_file():
        return None
    result = load_json(path)
    if result.get("schema") != RESULT_SCHEMA:
        raise CertError(f"{identifier} result schema must be {RESULT_SCHEMA}")
    if result.get("producer") != "agentpedia-verify-checks":
        raise CertError(f"{identifier} result was not produced by the check harness")
    if result.get("id") != identifier:
        raise CertError(f"{identifier} result id does not match the file")
    return result


def manifest_digest(identifier: str) -> str | None:
    path = CHECKS_DIR / f"{identifier}.json"
    if not path.is_file():
        return None
    return sha256_file(path)


def _review_error(review: object, today: date) -> str | None:
    """Return an error that must fail the build, or None when the review is well formed."""
    if not isinstance(review, dict):
        return "Certified requires a review object with reviewer, date, and notes."
    reviewer = str(review.get("reviewer") or "")
    reviewed = str(review.get("date") or "")
    notes = str(review.get("notes") or "").strip()
    if not LOGIN_RE.fullmatch(reviewer):
        return "review.reviewer must be a GitHub login."
    try:
        reviewed_on = parse_date(reviewed)
    except CertError:
        return "review.date must be YYYY-MM-DD."
    if reviewed_on > today:
        return "review.date is in the future."
    if not notes or len(notes) > 2000:
        return "review.notes must be 1 to 2000 characters."
    return None


def _run_problem(record: dict, result: dict | None, entry: dict, harness: str) -> str | None:
    """None when the run supports Verified. A 'pending:' or 'error:' prefix otherwise."""
    identifier = record["id"]
    if result is None:
        return "error:Verified requires certs/results/" + identifier + ".json from tools/verify_checks.py."
    if result.get("ok") is not True:
        return "error:The recorded check run did not pass. Re-run the harness or set the tier back to listed."
    if result.get("contentDigest") != record["contentDigest"]:
        return "error:The check result digest does not match the certificate record. Re-run verify_checks.py --write."
    if result.get("sourceCommit") != record["sourceCommit"]:
        return "error:The check result commit does not match the certificate record. Re-run verify_checks.py --write."
    if not isinstance(result.get("checks"), list) or not result["checks"]:
        return "error:The check result has no checks."
    kinds = {item.get("kind") for item in result["checks"] if isinstance(item, dict)}
    if "install" not in kinds or "eval" not in kinds:
        return "error:Verified requires an install probe and at least one eval."
    if any(item.get("ok") is not True for item in result["checks"]):
        return "error:A recorded check is not ok."
    if result.get("contentDigest") != entry["digest"]:
        return "pending:The entry files changed after the checks ran."
    if result.get("harnessDigest") != harness:
        return "pending:The check harness changed after this run."
    expected_manifest = manifest_digest(identifier)
    if result.get("manifestDigest") != expected_manifest:
        return "pending:The declared checks changed after this run."
    ran_at = str(result.get("ranAt") or "")
    if len(ran_at) < 10 or not DATE_RE.fullmatch(ran_at[:10]):
        return "error:The check result has no ranAt date."
    return None


def _checks_payload(result: dict | None) -> list[dict]:
    if not result:
        return []
    checks = []
    for item in result.get("checks") or []:
        if not isinstance(item, dict):
            continue
        checks.append(
            {
                "id": item.get("id"),
                "kind": item.get("kind"),
                "ok": bool(item.get("ok")),
                "exitCode": item.get("exitCode"),
                "durationMs": item.get("durationMs"),
                "stdout": item.get("stdout") or "",
                "stderr": item.get("stderr") or "",
            }
        )
    return checks


def _badge(display: str) -> tuple[str, dict]:
    message = BADGE_MESSAGE[display]
    message_bg, message_fg = BADGE_COLORS[display]
    label = "agentpedia"
    label_w = _text_width(label) + 12
    message_w = _text_width(message) + 12
    width = label_w + message_w
    height = 20
    title = f"{label}: {message}"
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'role="img" aria-label="{_xml(title)}">'
        f"<title>{_xml(title)}</title>"
        f'<g shape-rendering="crispEdges">'
        f'<rect width="{label_w}" height="{height}" fill="{LABEL_BG}"/>'
        f'<rect x="{label_w}" width="{message_w}" height="{height}" fill="{message_bg}"/>'
        f"</g>"
        f'<g font-family="Verdana,Geneva,DejaVu Sans,sans-serif" font-size="11" text-anchor="middle">'
        f'<text x="{label_w / 2:.1f}" y="14" fill="{LABEL_FG}">{_xml(label)}</text>'
        f'<text x="{label_w + message_w / 2:.1f}" y="14" fill="{message_fg}">{_xml(message)}</text>'
        f"</g></svg>\n"
    )
    meta = {"width": width, "height": height, "label": label, "message": message}
    return svg, meta


def _text_width(text: str) -> int:
    widths = {"i": 3, "l": 3, "j": 4, "f": 4, "t": 5, "r": 4, " ": 4, "-": 4, "m": 9, "w": 9}
    return sum(widths.get(char, 7) for char in text)


def _xml(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def evaluate_entry(entry: dict, record: dict, today: date, harness: str, result: object = _AUTO) -> dict:
    identifier = record["id"]
    if identifier != cert_id(entry["kind"], entry["name"]):
        raise CertError(f"{identifier} does not match {entry['source_path']}")
    claimed = record["tier"]
    if claimed == "certified":
        review_problem = _review_error(record.get("review"), today)
        if review_problem:
            raise CertError(f"{identifier}: {review_problem}")
    if result is _AUTO:
        if (RESULTS_DIR / f"{identifier}.json").is_file() or claimed in {"verified", "certified"}:
            result = load_result(identifier)
        else:
            result = None

    status = "active"
    reason = ""
    digest_matches = record["contentDigest"] == entry["digest"]
    lint_ok = qualifies(entry)

    if not digest_matches:
        status = "recheck-pending"
        reason = "The entry files changed after this certificate was issued."
    elif not lint_ok:
        status = "withheld"
        reason = "The lint score is below 100, so this certificate is not current."
    elif claimed in {"verified", "certified"}:
        problem = _run_problem(record, result, entry, harness)
        if problem:
            if problem.startswith("error:"):
                raise CertError(f"{identifier}: {problem[6:]}")
            status = "recheck-pending"
            reason = problem.split(":", 1)[1]
        elif _past(str(result["ranAt"])[:10], VERIFIED_DAYS, today):
            status = "expired"
            reason = "The verification run is past its 90-day revalidation date."
    if claimed == "certified" and status == "active" and _past(record["review"]["date"], REVIEW_DAYS, today):
        status = "expired"
        reason = "The human review is past its 365-day revalidation date."
    if claimed == "listed" and status == "active" and _past(record["issuedAt"], LISTED_DAYS, today):
        status = "expired"
        reason = "The listed certificate is past its 365-day revalidation date."

    if status == "active":
        if claimed == "listed":
            reason = "Listed. skill-lint scored 100 on the recorded files." if entry["kind"] == "skill" else (
                "Listed. The agent manifest is accepted and every bundled skill scores 100."
            )
        elif claimed == "verified":
            reason = "Verified. The install probe and declared evals passed in the check sandbox, and the lint score is 100."
        else:
            reason = "Certified. Verification is current and a human review is recorded."

    if claimed == "listed":
        expires = _expires(record["issuedAt"], LISTED_DAYS)
    elif claimed == "verified":
        start = str(result["ranAt"])[:10] if result and result.get("ranAt") else record["issuedAt"]
        expires = _expires(start, VERIFIED_DAYS)
    else:
        run_start = str(result["ranAt"])[:10] if result and result.get("ranAt") else record["issuedAt"]
        review = record.get("review") or {}
        review_start = str(review.get("date") or record["issuedAt"])
        run_end = _expires(run_start, VERIFIED_DAYS)
        review_end = _expires(review_start, REVIEW_DAYS)
        expires = run_end if run_end <= review_end else review_end

    display = claimed if status == "active" else status
    current_commit = entry["commit"] or record["sourceCommit"]
    review = record.get("review")
    if isinstance(review, dict):
        review_payload = {
            "reviewer": review.get("reviewer"),
            "date": review.get("date"),
            "notes": str(review.get("notes") or "").strip(),
        }
    else:
        review_payload = None

    counts = bool(
        claimed in {"verified", "certified"}
        and status == "active"
        and result
        and result.get("ok") is True
    )
    svg, badge = _badge(display)
    payload = {
        "schema": PAYLOAD_SCHEMA,
        "id": identifier,
        "subject": {
            "kind": entry["kind"],
            "name": entry["name"],
            "title": entry["title"],
            "sourcePath": entry["source_path"],
            "entryPath": entry_path(entry["kind"], entry["name"]),
        },
        "claimedTier": claimed,
        "displayTier": display,
        "status": status,
        "statusReason": reason,
        "sourceCommit": record["sourceCommit"],
        "currentCommit": current_commit,
        "contentDigest": record["contentDigest"],
        "currentDigest": entry["digest"],
        "issuedAt": record["issuedAt"],
        "expiresAt": expires,
        "revalidation": {
            "sourceRule": SOURCE_RULE,
            "expiryRule": EXPIRY_RULE,
            "listedDays": LISTED_DAYS,
            "verifiedDays": VERIFIED_DAYS,
            "reviewDays": REVIEW_DAYS,
        },
        "lint": entry["lint"],
        "review": review_payload,
        "run": {
            "present": result is not None,
            "ok": bool(result and result.get("ok") is True),
            "ranAt": (result or {}).get("ranAt") if result else None,
            "countsAsVerification": counts,
            "harnessDigest": (result or {}).get("harnessDigest") if result else None,
            "manifestDigest": (result or {}).get("manifestDigest") if result else None,
        },
        "checks": _checks_payload(result) if result else [],
        "limits": LIMITS,
        "badge": badge,
        "urls": _record_urls(identifier),
    }
    return {"payload": payload, "svg": svg}


def _prepare_entry(entry: dict) -> dict:
    directory = ROOT / entry["source_path"]
    prepared = dict(entry)
    prepared["digest"] = content_digest(directory)
    prepared["commit"] = git_commit(ROOT, directory)
    return prepared


def _record_urls(identifier: str) -> dict:
    origin = site_origin()
    return {
        "page": f"{origin}/cert/{identifier}",
        "badge": f"{origin}/badge/{identifier}.svg",
        "record": f"{origin}/cert/{identifier}.json",
        "publicKey": f"{origin}/.well-known/agentpedia-signing-key.json",
    }


def _signing_key_document(signed: bool) -> dict:
    pinned = None
    if PUBLIC_KEY_PATH.is_file():
        pinned = load_json(PUBLIC_KEY_PATH)
    keys = []
    if pinned and pinned.get("publicKeyPem"):
        keys.append(
            {
                "kid": pinned.get("kid") or "primary",
                "alg": "Ed25519",
                "publicKeyPem": pinned["publicKeyPem"],
            }
        )
    if signed:
        note = "This build signed every certificate with AGENTPEDIA_SIGNING_KEY."
    elif keys:
        note = (
            "A public key is pinned in certs/public-key.json, but AGENTPEDIA_SIGNING_KEY "
            "was unset, so these records are unsigned."
        )
    else:
        note = "AGENTPEDIA_SIGNING_KEY was unset and no public key is pinned. These records are unsigned."
    return {
        "schema": KEY_SCHEMA,
        "configured": signed,
        "pinned": bool(keys),
        "alg": "Ed25519",
        "url": f"{site_origin()}/.well-known/agentpedia-signing-key.json",
        "keys": keys,
        "note": note,
    }


def _reset_public_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def publish_certificates(entries: list[dict]) -> dict:
    """Issue missing Listed records, evaluate every claim, and write the site files."""
    today = parse_date(today_iso())
    try:
        created = ensure_listed_records(entries, today.isoformat())
    except CertError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    if created:
        print(f"issued {len(created)} listed certificate(s)")

    records = load_records()
    harness = sha256_file(HARNESS_PATH) if HARNESS_PATH.is_file() else ""
    prepared = [_prepare_entry(entry) for entry in entries]
    known = {cert_id(entry["kind"], entry["name"]): entry for entry in prepared}
    errors: list[str] = []
    published: list[dict] = []
    svgs: dict[str, str] = {}

    for identifier, record in records.items():
        entry = known.get(identifier)
        if entry is None:
            errors.append(f"{identifier} does not match a skill or an agent")
            continue
        try:
            evaluated = evaluate_entry(entry, record, today, harness)
        except CertError as exc:
            errors.append(str(exc))
            continue
        svg = evaluated.pop("svg")
        payload = evaluated["payload"]
        document = {
            "payload": payload,
            "canonical": canonical(payload),
            "signed": False,
            "signature": None,
            "keyUrl": payload["urls"]["publicKey"],
        }
        published.append(document)
        svgs[identifier] = svg

    missing = [
        cert_id(entry["kind"], entry["name"])
        for entry in prepared
        if qualifies(entry) and cert_id(entry["kind"], entry["name"]) not in records
    ]
    for identifier in missing:
        errors.append(f"{identifier} passes the lint gate and has no certificate record")

    if errors:
        for message in errors:
            print(f"error: {message}", file=sys.stderr)
        raise SystemExit(1)

    published.sort(key=lambda item: item["payload"]["id"])
    stats = {
        "total": len(published),
        "active": sum(1 for item in published if item["payload"]["status"] == "active"),
        "listed": sum(1 for item in published if item["payload"]["displayTier"] == "listed"),
        "verified": sum(1 for item in published if item["payload"]["displayTier"] == "verified"),
        "certified": sum(1 for item in published if item["payload"]["displayTier"] == "certified"),
        "recheckPending": sum(1 for item in published if item["payload"]["status"] == "recheck-pending"),
        "expired": sum(1 for item in published if item["payload"]["status"] == "expired"),
        "withheld": sum(1 for item in published if item["payload"]["status"] == "withheld"),
    }
    catalog = {
        "schema": SET_SCHEMA,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "rules": {
            "listedDays": LISTED_DAYS,
            "verifiedDays": VERIFIED_DAYS,
            "reviewDays": REVIEW_DAYS,
        },
        "signing": {"alg": "Ed25519", "signed": False},
        "stats": stats,
        "certificates": published,
    }
    dump_json(DATA_PATH, catalog)
    _reset_public_dir(BADGE_DIR)
    _reset_public_dir(CERT_PUBLIC_DIR)
    for document in published:
        identifier = document["payload"]["id"]
        (BADGE_DIR / f"{identifier}.svg").write_text(svgs[identifier], encoding="utf-8")
        dump_json(CERT_PUBLIC_DIR / f"{identifier}.json", document)
    dump_json(WELL_KNOWN_PATH, _signing_key_document(False))
    print(
        f"certificates: {stats['listed']} listed, {stats['verified']} verified, "
        f"{stats['certified']} certified, {stats['recheckPending']} re-check pending, "
        f"{stats['expired']} expired"
    )
    print(f"wrote {DATA_PATH.relative_to(ROOT)}")
    return catalog


def save_record(record: dict) -> None:
    validate_record_shape(record, record["id"])
    dump_json(RECORDS_DIR / f"{record['id']}.json", record)
