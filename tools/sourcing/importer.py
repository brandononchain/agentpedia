"""Import one upstream skill, or the next queued rows, into the catalog.

A row is accepted only when the license is on the allow list, skill-lint scores
100, and the static audit is not on hold and not grade F. Anything else is left
out of the tree and marked rejected on the candidate row.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "skill-lint"))

from skill_lint.frontmatter import split_frontmatter  # noqa: E402
from skill_lint.rules import NAME_RE, lint_skill  # noqa: E402
from sourcing.adapt import adapt_skill, choose_subshelf, copyright_line_from, guess_shelf, resolve_author  # noqa: E402
from sourcing.candidate_queue import (  # noqa: E402
    is_rejected_family,
    license_decision,
    load_queue,
    row_key,
    save_queue,
    select_next,
    shelf_counts,
    slug,
    update_row,
)

QUEUE_PATH = ROOT / "data" / "candidates.json"
NOTICE_PATH = ROOT / "NOTICE"
BLOB_RE = re.compile(
    r"^https?://github\.com/([^/]+)/([^/#]+?)(?:\.git)?/(?:blob|tree)/([^/]+)/(.+?)/?$",
    re.IGNORECASE,
)
REPO_RE = re.compile(r"^https?://github\.com/([^/]+)/([^/#]+?)(?:\.git)?/?$", re.IGNORECASE)
LICENSE_NAMES = ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING", "COPYING.txt")


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def gh_api(path: str, raw: bool = False) -> tuple[int, str]:
    command = ["gh", "api"]
    if raw:
        command.extend(["-H", "Accept: application/vnd.github.raw"])
    command.append(path)
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return 0, "timeout"
    if proc.returncode != 0:
        err = (proc.stderr or "") + (proc.stdout or "")
        if "404" in err or "Not Found" in err:
            return 404, err.strip()
        return proc.returncode or 1, err.strip()
    return 200, proc.stdout


def parse_github_url(url: str) -> tuple[str, str, str]:
    """Return (repo, ref, path). ref and path are empty for a bare repo URL."""
    text = url.strip()
    match = BLOB_RE.match(text)
    if match:
        owner, name, ref, path = match.groups()
        return f"{owner}/{name}", urllib.parse.unquote(ref), urllib.parse.unquote(path)
    match = REPO_RE.match(text)
    if match:
        return f"{match.group(1)}/{match.group(2)}", "", ""
    raise ValueError(f"not a GitHub blob, tree, or repo URL: {url}")


def resolve_sha(repo: str, ref: str) -> str:
    status, body = gh_api(f"repos/{repo}/commits/{urllib.parse.quote(ref, safe='')}")
    if status != 200:
        raise RuntimeError(f"could not pin {repo}@{ref}: {body[:180]}")
    data = json.loads(body)
    sha = str(data.get("sha") or "")
    if not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise RuntimeError(f"no commit sha for {repo}@{ref}")
    return sha


def repo_facts(repo: str) -> dict:
    status, body = gh_api(f"repos/{repo}")
    if status != 200:
        raise RuntimeError(f"could not read {repo}: {body[:180]}")
    data = json.loads(body)
    owner = data.get("owner") or {}
    license_info = data.get("license") or {}
    spdx = license_info.get("spdx_id") or ""
    if spdx in {"NOASSERTION", "OTHER", None}:
        spdx = ""
    return {
        "default_branch": data.get("default_branch") or "main",
        "spdx": spdx,
        "owner_login": owner.get("login") or repo.split("/")[0],
        "owner_type": owner.get("type") or "User",
        "description": data.get("description") or "",
    }


def profile_name(login: str) -> str:
    status, body = gh_api(f"users/{urllib.parse.quote(login)}")
    if status != 200:
        return ""
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return ""
    name = data.get("name") or ""
    return name if isinstance(name, str) else ""


def fetch_text(repo: str, sha: str, path: str) -> str | None:
    quoted = urllib.parse.quote(path, safe="/")
    status, body = gh_api(f"repos/{repo}/contents/{quoted}?ref={sha}", raw=True)
    if status != 200:
        return None
    if body.lstrip().startswith('{"message"'):
        return None
    return body


def fetch_license(repo: str, sha: str) -> str:
    for name in LICENSE_NAMES:
        text = fetch_text(repo, sha, name)
        if text and "Not Found" not in text[:80]:
            return text
    return ""


def find_skill_path(repo: str, sha: str, hint: str) -> str:
    status, body = gh_api(f"repos/{repo}/git/trees/{sha}?recursive=1")
    if status != 200:
        raise RuntimeError(f"could not list {repo}@{sha[:7]}")
    tree = json.loads(body).get("tree") or []
    paths = []
    for node in tree:
        path = node.get("path") or ""
        if node.get("type") == "blob" and path.endswith("SKILL.md"):
            paths.append(path)
    if not paths:
        raise RuntimeError(f"{repo} has no SKILL.md at {sha[:7]}")
    hint_slug = slug(hint)
    for path in paths:
        folder = Path(path).parent.name
        if slug(folder) == hint_slug or hint_slug in slug(path):
            return path
    if len(paths) == 1:
        return paths[0]
    raise RuntimeError(f"{repo} has {len(paths)} SKILL.md files; pass a blob URL")


def frontmatter_author(fields: dict) -> str:
    for key in ("author", "authors"):
        value = fields.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    metadata = fields.get("metadata")
    if isinstance(metadata, dict):
        for key in ("author", "authors"):
            value = metadata.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return ""


def catalog_skill_text(name: str) -> str | None:
    for path in (ROOT / "skills").glob(f"*/{name}/SKILL.md"):
        return path.read_text(encoding="utf-8")
    return None


def texts_differ(left: str, right: str) -> bool:
    def norm(text: str) -> set[str]:
        text = re.sub(r"^---.*?---", " ", text, count=1, flags=re.S)
        words = re.findall(r"[a-z0-9]{4,}", text.lower())
        return set(words)

    a, b = norm(left), norm(right)
    if not a or not b:
        return True
    overlap = len(a & b) / min(len(a), len(b))
    return overlap < 0.75


def load_allowed() -> dict[str, list[str]]:
    allowed: dict[str, list[str]] = {}
    for meta in (ROOT / "skills").glob("*/category.json"):
        data = json.loads(meta.read_text(encoding="utf-8"))
        allowed[meta.parent.name] = [
            str(item.get("slug"))
            for item in data.get("subshelves") or []
            if isinstance(item, dict) and item.get("slug")
        ]
    return allowed


def lint_ok(folder: Path) -> tuple[bool, str]:
    report = lint_skill(folder / "SKILL.md")
    penalty = report.error_count * 25 + report.warn_count * 8 + report.info_count * 2
    score = max(0, 100 - penalty)
    if score == 100 and not report.findings:
        return True, "lint 100"
    detail = "; ".join(f"{item.severity} {item.rule_id}: {item.message}" for item in report.findings[:6])
    return False, f"lint {score}: {detail}"


def audit_ok(folder: Path, entry_id: str) -> tuple[bool, str]:
    from audit.engine import audit_directory, public_view
    from audit.grace import load_ledger
    from certlib import content_digest, today_iso

    findings, lock, cve = audit_directory(folder)
    view = public_view(
        findings,
        lock=lock,
        content_digest=content_digest(folder),
        commit="",
        ledger=load_ledger(ROOT),
        entry_id=entry_id,
        today=today_iso(),
        cve_lookup=cve,
    )
    if view["status"] == "on-hold" or view["grade"] == "F":
        return False, f"audit {view['status']} grade {view['grade']}: {view['summary']}"
    return True, f"audit {view['status']} {view['grade']} {view['score']}"


def append_notice(name: str, copyright_line: str, license_id: str, url: str) -> None:
    text = NOTICE_PATH.read_text(encoding="utf-8")
    if url in text:
        return
    heading = "Upstream skills adapted into this catalog:\n"
    if heading not in text:
        if not text.endswith("\n"):
            text += "\n"
        text += "\n" + heading + "\n"
    block = f"- {name}, {copyright_line}, {license_id}\n  Source: {url}\n"
    NOTICE_PATH.write_text(text + block, encoding="utf-8")


def blob_url(repo: str, sha: str, path: str) -> str:
    return f"https://github.com/{repo}/blob/{sha}/{path}"


class ImportResult:
    def __init__(self, name: str, status: str, reason: str, shelf: str = "", license_id: str = "", url: str = ""):
        self.name = name
        self.status = status
        self.reason = reason
        self.shelf = shelf
        self.license_id = license_id
        self.url = url


def import_one(
    source: str,
    *,
    shelf_override: str = "",
    queue_row: dict | None = None,
) -> ImportResult:
    try:
        repo, ref, path = parse_github_url(source)
    except ValueError as exc:
        return ImportResult(slug(source), "rejected", str(exc))
    label = (queue_row or {}).get("name") or path or repo
    try:
        facts = repo_facts(repo)
        pinned_ref = ref or facts["default_branch"]
        sha = resolve_sha(repo, pinned_ref)
        if not path:
            path = (queue_row or {}).get("path") or ""
        if not path or not path.lower().endswith("skill.md"):
            path = find_skill_path(repo, sha, (queue_row or {}).get("name") or "")
        queue_state = (queue_row or {}).get("licenseState") or ""
        if queue_state == "copyleft" or is_rejected_family((queue_row or {}).get("license")):
            return ImportResult(label, "rejected", "license is copyleft and cannot be imported", url=source)
        license_file = fetch_license(repo, sha)
        license_id, license_reason = license_decision(facts["spdx"], license_file, queue_state)
        if not license_id:
            return ImportResult(label, "rejected", license_reason, url=blob_url(repo, sha, path))
        skill_text = fetch_text(repo, sha, path)
        if not skill_text or not skill_text.strip():
            return ImportResult(label, "rejected", f"SKILL.md missing at {path}", url=blob_url(repo, sha, path))
    except RuntimeError as exc:
        return ImportResult(label, "rejected", str(exc), url=source)

    front = split_frontmatter(skill_text)
    raw_name = ""
    description = ""
    if front.fields and not front.parse_error:
        raw_name = str(front.fields.get("name") or "")
        description = str(front.fields.get("description") or "")
    name = slug(raw_name or Path(path).parent.name or (queue_row or {}).get("name") or "")
    if not NAME_RE.fullmatch(name):
        return ImportResult(name or label, "rejected", f"name {name!r} is not a catalog id", url=blob_url(repo, sha, path))
    existing = catalog_skill_text(name)
    if existing is not None:
        if not texts_differ(existing, skill_text):
            return ImportResult(name, "rejected", f"name collision with {name}; the text matches an entry already in the catalog", url=blob_url(repo, sha, path))
        owner = repo.split("/")[0].lower()
        renamed = slug(f"{name}-{owner}")
        if catalog_skill_text(renamed) is not None:
            return ImportResult(name, "rejected", f"name collision with {name} and {renamed} is taken", url=blob_url(repo, sha, path))
        name = renamed
    stated_author = frontmatter_author(front.fields) if front.fields else ""
    author, author_url, author_kind = resolve_author(
        facts["owner_login"],
        facts["owner_type"],
        profile_name(facts["owner_login"]),
        license_file,
        stated_author,
    )
    allowed = load_allowed()
    shelf = shelf_override or (queue_row or {}).get("shelf") or guess_shelf(name, description, path)
    if shelf not in allowed:
        shelf = guess_shelf(name, description, path)
    if shelf not in allowed:
        return ImportResult(name, "rejected", f"no shelf named {shelf}", url=blob_url(repo, sha, path))
    subshelf = choose_subshelf(shelf, name, description, path, allowed[shelf])
    copyright_line = copyright_line_from(license_file, author)
    markdown = adapt_skill(
        name=name,
        upstream_text=skill_text,
        description=description or facts["description"] or name.replace("-", " "),
        shelf=shelf,
        subshelf=subshelf,
        author=author,
        author_url=author_url,
        author_kind=author_kind,
        license_id=license_id,
        repo=repo,
        commit=sha,
        upstream_path=path,
        copyright_line=copyright_line,
    )
    folder = ROOT / "skills" / shelf / name
    if folder.exists():
        return ImportResult(name, "rejected", f"{folder.relative_to(ROOT)} already exists", url=blob_url(repo, sha, path))
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(markdown, encoding="utf-8")
    ok, lint_reason = lint_ok(folder)
    if not ok:
        shutil.rmtree(folder)
        return ImportResult(name, "rejected", lint_reason, url=blob_url(repo, sha, path))
    passed, audit_reason = audit_ok(folder, f"skill-{name}")
    if not passed:
        shutil.rmtree(folder)
        return ImportResult(name, "rejected", audit_reason, url=blob_url(repo, sha, path))
    url = blob_url(repo, sha, path)
    append_notice(name, copyright_line, license_id, url)
    print(f"imported {shelf}/{name} from {repo}@{sha[:7]} ({license_id}); author {author}; {lint_reason}; {audit_reason}")
    return ImportResult(name, "imported", f"skills/{shelf}/{name}", shelf=shelf, license_id=license_id, url=url)


def _mark(document: dict, source: str, row: dict | None, result: ImportResult) -> None:
    reason = result.reason if result.status == "rejected" else result.reason
    if result.status == "imported":
        reason = f"imported to {result.reason}"
    rows = document.setdefault("candidates", [])
    key = row_key(row) if row else ""
    if not key and row is None:
        # Match a queued row by URL or repo path when --from was typed by hand.
        for candidate in rows:
            if candidate.get("sourceUrl") == source or (result.url and candidate.get("sourceUrl") == result.url):
                key = row_key(candidate)
                break
    if key:
        update_row(rows, key, result.status if result.status in {"imported", "rejected"} else "rejected", reason)


def refresh_index() -> None:
    subprocess.check_call([sys.executable, str(ROOT / "tools" / "build_index.py")], cwd=ROOT)


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Import a licensed upstream skill into Agentpedia.")
    parser.add_argument("--from", dest="source", default="", help="GitHub blob URL or repo URL")
    parser.add_argument("--shelf", default="", help="Shelf id. Defaults to the queue guess.")
    parser.add_argument("--next", dest="count", type=int, default=0, help="Import this many queued compatible skills")
    parser.add_argument(
        "--prefer-empty-shelves",
        action="store_true",
        help="Take Education, Product, and People first, then other thin shelves, and prefer official orgs",
    )
    parser.add_argument("--queue", type=Path, default=QUEUE_PATH)
    args = parser.parse_args(argv)
    if not args.source and args.count <= 0:
        fail("pass --from <url> or --next N")
    document = load_queue(args.queue)
    results: list[ImportResult] = []
    if args.source:
        matched = next((row for row in document["candidates"] if row.get("sourceUrl") == args.source), None)
        result = import_one(args.source, shelf_override=args.shelf, queue_row=matched)
        results.append(result)
        _mark(document, args.source, matched, result)
    if args.count > 0:
        order = select_next(document["candidates"], shelf_counts(ROOT / "skills"), args.prefer_empty_shelves)
        imported = sum(1 for item in results if item.status == "imported")
        for row in order:
            if imported >= args.count:
                break
            if row.get("status") != "queued":
                continue
            result = import_one(row.get("sourceUrl") or f"https://github.com/{row.get('repo')}", queue_row=row)
            results.append(result)
            _mark(document, row.get("sourceUrl") or "", row, result)
            if result.status == "imported":
                imported += 1
    save_queue(args.queue, document)
    accepted = [item for item in results if item.status == "imported"]
    rejected = [item for item in results if item.status == "rejected"]
    if accepted:
        refresh_index()
    print(f"imported {len(accepted)}, rejected {len(rejected)}")
    for item in rejected:
        print(f"rejected {item.name}: {item.reason}")
    if args.count and len(accepted) < args.count and not args.source:
        return 1
    if args.source and not accepted and rejected:
        return 1
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
