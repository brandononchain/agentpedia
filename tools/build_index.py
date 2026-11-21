#!/usr/bin/env python3
"""Lint every skill and write the catalog the site is built from.

Fails if any skill has a lint error or warning. Info findings are kept,
counted, and reflected in the score. Agent manifests are checked for
required fields and for skill names that exist.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "skill-lint"))

from skill_lint.frontmatter import split_frontmatter  # noqa: E402
from skill_lint.rules import lint_skill  # noqa: E402
from skill_lint.shelf_case import shelf_label_error  # noqa: E402

SKILLS_DIR = ROOT / "skills"
AGENTS_DIR = ROOT / "agents"
DATA_PATH = ROOT / "data" / "catalog.json"
RAW_DIR = ROOT / "public" / "raw"
REPO_URL = "https://github.com/brandononchain/agentpedia"
REPO_DIR = REPO_URL.rstrip("/").rsplit("/", 1)[-1]
LINK_RE = re.compile(r"(!?)\[([^\]]*)\]\(([^)]+)\)")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

RULES = [
    {
        "group": "Spec",
        "rules": [
            ["spec.frontmatter.missing", "error", "File must start with YAML frontmatter between --- lines."],
            ["spec.frontmatter.invalid", "error", "Frontmatter must parse as simple YAML keys."],
            ["spec.filename.case", "error", "The file must be named SKILL.md. Linux treats the name as case-sensitive."],
            ["spec.name.missing", "error", "name is required and must be non-empty."],
            ["spec.name.invalid", "error", "name is lowercase letters, numbers, and single hyphens. No leading, trailing, or doubled hyphens."],
            ["spec.name.too-long", "error", "name is at most 64 characters."],
            ["spec.name.directory-mismatch", "error", "name must match the parent folder exactly."],
            ["spec.description.missing", "error", "description is required and must be non-empty."],
            ["spec.description.too-long", "error", "description is at most 1024 characters."],
            ["spec.compatibility.too-long", "error", "compatibility is at most 500 characters."],
        ],
    },
    {
        "group": "Smells",
        "rules": [
            ["smell.name.unclear", "warn", "Name is generic (helper, misc, skill, …) or shorter than 3 characters."],
            ["smell.description.no-when", "warn", "Description does not say when to use the skill."],
            ["smell.description.vague", "warn", "Description is under 40 characters."],
            ["smell.description.not-third-person", "info", "Description uses I/you phrasing. Third person matches more reliably."],
            ["smell.description.xml", "error", "Description contains XML or HTML tags."],
            ["smell.body.too-long-lines", "warn", "Body is longer than 500 lines. Move detail into references/."],
            ["smell.body.too-long-words", "warn", "Body is longer than 5000 words."],
            ["smell.body.huge-inline-blob", "warn", "A fenced block is 80 lines or longer. Move it to references/ or scripts/."],
            ["smell.example.missing", "warn", "Body has no example of an input, an output, or a usage."],
            ["smell.workflow.stepless", "warn", "A longer body has no numbered steps."],
            ["smell.validation.missing", "info", "Body never mentions a check, a test, or validation."],
            ["smell.scripts.missing", "info", "Many shell commands and no scripts/ helpers."],
            ["smell.detail.undelegated", "warn", "A very long body does not delegate detail to references/."],
        ],
    },
    {
        "group": "Links",
        "rules": [
            ["link.relative.missing", "error", "A relative link or scripts/, references/, assets/, or lib/ path does not exist."],
            ["link.path.backslash", "warn", "A path uses backslashes. Skill trees are POSIX."],
        ],
    },
    {
        "group": "Safety",
        "rules": [
            ["security.secret", "error", "A hardcoded credential, token, or private key."],
            ["security.curl-pipe-sh", "error", "A download piped directly into a shell."],
            ["security.rm-rf", "warn", "rm -rf. This is an error when aimed at /, /*, or the home directory."],
            ["security.absolute-path", "warn", "A machine-specific absolute path such as /Users, /home, or a drive letter."],
            ["security.exfil-url", "warn", "A URL that looks like a webhook, tunnel, or paste-site sink."],
        ],
    },
    {
        "group": "Scan",
        "rules": [
            ["scan.path.missing", "error", "The path passed to the linter does not exist."],
            ["scan.skill.not-found", "error", "No SKILL.md file was found under the path."],
            ["scan.file.unreadable", "error", "A skill file could not be read as UTF-8."],
        ],
    },
]

SCORING = {
    "start": 100,
    "errorPenalty": 25,
    "warningPenalty": 8,
    "infoPenalty": 2,
    "floor": 0,
}


def score_for(errors: int, warnings: int, info: int) -> int:
    raw = (
        SCORING["start"]
        - errors * SCORING["errorPenalty"]
        - warnings * SCORING["warningPenalty"]
        - info * SCORING["infoPenalty"]
    )
    return max(SCORING["floor"], raw)


def badge_for(errors: int, warnings: int) -> str:
    if errors:
        return "blocked"
    if warnings:
        return "noted"
    return "clean"


def read_category(folder: Path) -> dict:
    meta_path = folder / "category.json"
    if not meta_path.is_file():
        raise SystemExit(f"missing {meta_path.relative_to(ROOT)} with label and blurb")
    try:
        data = json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON in {meta_path}: {exc}") from exc
    label = str(data.get("label") or "").strip()
    blurb = str(data.get("blurb") or "").strip()
    if not label or not blurb:
        raise SystemExit(f"{meta_path.relative_to(ROOT)} needs label and blurb")
    reason = shelf_label_error(label)
    if reason:
        raise SystemExit(f"{meta_path.relative_to(ROOT)} label is not title case: {reason}")
    number = data.get("number")
    if not isinstance(number, int) or number < 1:
        raise SystemExit(f"{meta_path.relative_to(ROOT)} needs a positive integer number")
    raw_subs = data.get("subshelves")
    if not isinstance(raw_subs, list) or not raw_subs:
        raise SystemExit(f"{meta_path.relative_to(ROOT)} needs a subshelves list")
    subshelves = []
    seen = set()
    for index, item in enumerate(raw_subs, start=1):
        if not isinstance(item, dict):
            raise SystemExit(f"{meta_path.relative_to(ROOT)} subshelf {index} is not an object")
        slug = str(item.get("slug") or "").strip()
        sub_label = str(item.get("label") or "").strip()
        description = str(item.get("description") or "").strip()
        if not slug or not sub_label or not description:
            raise SystemExit(f"{meta_path.relative_to(ROOT)} subshelf {index} needs slug, label, and description")
        if slug in seen:
            raise SystemExit(f"{meta_path.relative_to(ROOT)} repeats subshelf {slug}")
        seen.add(slug)
        sub_reason = shelf_label_error(sub_label)
        if sub_reason:
            raise SystemExit(f"{meta_path.relative_to(ROOT)} subshelf {slug} is not title case: {sub_reason}")
        subshelves.append(
            {"slug": slug, "label": sub_label, "description": description, "number": index, "count": 0}
        )
    return {
        "id": folder.name,
        "label": label,
        "blurb": blurb,
        "number": number,
        "subshelves": subshelves,
    }


def field(fields: dict, key: str) -> str:
    value = fields.get(key, "")
    if isinstance(value, dict):
        return ""
    return str(value or "").strip()


def meta_value(fields: dict, key: str) -> str:
    metadata = fields.get("metadata")
    if not isinstance(metadata, dict):
        return ""
    return str(metadata.get(key) or "").strip()


DEFAULT_AUTHOR = "Brandon"
DEFAULT_AUTHOR_URL = "https://github.com/brandononchain"


def credit_fields(fields: dict, nested: bool) -> dict[str, object]:
    """Author is the person or org who wrote the entry. Curator is set for imports and inbound submissions."""

    def pick(key: str) -> str:
        if nested:
            return meta_value(fields, key)
        return field(fields, key) or meta_value(fields, key)

    author = pick("author") or DEFAULT_AUTHOR
    author_url = pick("authorUrl") or DEFAULT_AUTHOR_URL
    author_kind = pick("authorKind") or "person"
    if author_kind not in {"person", "organization"}:
        author_kind = "person"
    repo = pick("upstream")
    commit = pick("upstreamCommit")
    path = pick("upstreamPath")
    upstream_license = pick("upstreamLicense") or field(fields, "license")
    upstream = None
    if repo and commit:
        url = (
            f"https://github.com/{repo}/blob/{commit}/{path}"
            if path
            else f"https://github.com/{repo}/commit/{commit}"
        )
        upstream = {
            "repo": repo,
            "commit": commit,
            "path": path,
            "license": upstream_license,
            "url": url,
        }
    return {
        "author": author,
        "authorUrl": author_url,
        "authorKind": author_kind,
        "curator": pick("curator"),
        "source": pick("source"),
        "upstream": upstream,
    }


def split_list(value: str, comma: bool = False) -> list[str]:
    text = value.strip()
    if not text or text.lower() == "none":
        return []
    if " || " in text:
        return [part.strip() for part in text.split(" || ") if part.strip()]
    if comma:
        return [part.strip() for part in text.split(",") if part.strip()]
    return [text]


def rewrite_links(body: str, category: str, name: str) -> str:
    def repl(match: re.Match[str]) -> str:
        bang, text, raw = match.group(1), match.group(2), match.group(3).strip()
        target = raw.strip("<>").strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "tel:", "#")):
            return match.group(0)
        path_and_query = target.split("#", 1)
        path_part = path_and_query[0].split("?", 1)[0].strip()
        anchor = f"#{path_and_query[1]}" if len(path_and_query) == 2 else ""
        if not path_part or path_part.endswith("/"):
            return match.group(0)
        url = f"/raw/skills/{category}/{name}/{path_part}{anchor}"
        return f"{bang}[{text}]({url})"

    return LINK_RE.sub(repl, body)


def title_from_body(body: str, fallback: str) -> str:
    for line in body.splitlines():
        if line.startswith("# "):
            return line[2:].strip() or fallback
    return fallback


def install_snippet(category: str, name: str, dest: str) -> str:
    return (
        f"# From a checkout of this repo\n"
        f"mkdir -p {dest}\n"
        f"cp -R skills/{category}/{name}/. {dest}\n"
        f"\n"
        f"# Or clone, then copy\n"
        f"git clone --depth 1 {REPO_URL}.git\n"
        f"mkdir -p {dest}\n"
        f"cp -R {REPO_DIR}/skills/{category}/{name}/. {dest}\n"
    )


def install_for(category: str, name: str) -> dict[str, dict[str, str]]:
    return {
        "claude": {
            "label": "Claude Code",
            "hint": "Project skills live in .claude/skills. For every project on the machine, use $HOME/.claude/skills instead.",
            "snippet": install_snippet(category, name, f".claude/skills/{name}"),
        },
        "codex": {
            "label": "Codex",
            "hint": "Codex reads .codex/skills in the project, or $HOME/.codex/skills for a personal install.",
            "snippet": install_snippet(category, name, f".codex/skills/{name}"),
        },
        "cursor": {
            "label": "Cursor",
            "hint": "Put the folder in .cursor/skills so Cursor can load the SKILL.md on demand.",
            "snippet": install_snippet(category, name, f".cursor/skills/{name}"),
        },
        "grok": {
            "label": "Grok Bot",
            "hint": "Agent SDK bots load skills from bot/skills. Copy the folder there and keep the name.",
            "snippet": install_snippet(category, name, f"bot/skills/{name}"),
        },
    }


def copy_raw(skill_dir: Path, category: str, name: str) -> None:
    dest = RAW_DIR / "skills" / category / name
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(
        skill_dir,
        dest,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    zip_path = RAW_DIR / "zips" / f"{name}.zip"
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(skill_dir.rglob("*")):
            if not file.is_file() or "__pycache__" in file.parts or file.suffix == ".pyc":
                continue
            archive.write(file, arcname=str(Path(name) / file.relative_to(skill_dir)))


def file_tree(skill_dir: Path, category: str, name: str) -> list[dict[str, object]]:
    files = []
    for file in sorted(skill_dir.rglob("*")):
        if not file.is_file() or "__pycache__" in file.parts or file.suffix == ".pyc":
            continue
        rel = file.relative_to(skill_dir).as_posix()
        files.append(
            {
                "path": rel,
                "bytes": file.stat().st_size,
                "url": f"/raw/skills/{category}/{name}/{rel}",
            }
        )
    return files


def finding_payload(finding) -> dict[str, object]:
    try:
        rel = Path(finding.path).resolve().relative_to(ROOT).as_posix()
    except ValueError:
        rel = Path(finding.path).name
    return {
        "ruleId": finding.rule_id,
        "severity": finding.severity,
        "message": finding.message,
        "hint": finding.hint,
        "line": finding.line,
        "path": rel,
    }


def load_shelves() -> list[dict]:
    if not SKILLS_DIR.is_dir():
        raise SystemExit("skills/ directory is missing")
    shelves = []
    for folder in sorted(path for path in SKILLS_DIR.iterdir() if (path / "category.json").is_file()):
        shelves.append(read_category(folder))
    numbers = [item["number"] for item in shelves]
    if len(numbers) != len(set(numbers)):
        raise SystemExit("shelf numbers must be unique")
    return shelves


def load_skills() -> tuple[list[dict], list[str]]:
    problems: list[str] = []
    skills: list[dict] = []
    if not SKILLS_DIR.is_dir():
        raise SystemExit("skills/ is missing")
    for category_dir in sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir()):
        meta = read_category(category_dir)
        label, blurb = meta["label"], meta["blurb"]
        category = category_dir.name
        allowed = {item["slug"]: item for item in meta["subshelves"]}
        for skill_dir in sorted(path for path in category_dir.iterdir() if path.is_dir()):
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.is_file():
                problems.append(f"{skill_dir.relative_to(ROOT)} has no SKILL.md")
                continue
            report = lint_skill(skill_file)
            text = skill_file.read_text(encoding="utf-8")
            front = split_frontmatter(text)
            name = field(front.fields, "name") or skill_dir.name
            if name != skill_dir.name:
                problems.append(f"{skill_file.relative_to(ROOT)} name does not match its folder")
            added = meta_value(front.fields, "added")
            if not ISO_DATE.fullmatch(added):
                problems.append(f"{name} metadata.added must be YYYY-MM-DD")
            declared = meta_value(front.fields, "category")
            if declared and declared != category:
                problems.append(f"{name} metadata.category is {declared}, folder is {category}")
            subshelf = meta_value(front.fields, "subshelf")
            sub = allowed.get(subshelf)
            if sub is None:
                problems.append(f"{name} metadata.subshelf must be one of: {', '.join(allowed)}")
            errors = report.error_count
            warnings = report.warn_count
            info = report.info_count
            description = field(front.fields, "description")
            body = front.body.strip() + "\n"
            copy_raw(skill_dir, category, name)
            skills.append(
                {
                    "name": name,
                    "title": title_from_body(body, name),
                    "description": description,
                    "category": category,
                    "categoryLabel": label,
                    "categoryBlurb": blurb,
                    "shelfNumber": meta["number"],
                    "subshelf": subshelf,
                    "subshelfLabel": sub["label"] if sub else "",
                    "callNumber": f"{meta['number']}.{sub['number']}" if sub else "",
                    "tags": split_list(meta_value(front.fields, "tags"), comma=True),
                    "added": added,
                    "featured": meta_value(front.fields, "featured").lower() == "true",
                    "license": field(front.fields, "license") or "Apache-2.0",
                    "compatibility": field(front.fields, "compatibility"),
                    **credit_fields(front.fields, nested=True),
                    "lint": {
                        "score": score_for(errors, warnings, info),
                        "errors": errors,
                        "warnings": warnings,
                        "info": info,
                        "badge": badge_for(errors, warnings),
                        "findings": [finding_payload(item) for item in report.findings],
                    },
                    "files": file_tree(skill_dir, category, name),
                    "body": rewrite_links(body, category, name),
                    "install": install_for(category, name),
                    "rawUrl": f"/raw/skills/{category}/{name}/SKILL.md",
                    "zipUrl": f"/raw/zips/{name}.zip",
                    "sourcePath": skill_dir.relative_to(ROOT).as_posix(),
                }
            )
    names = [item["name"] for item in skills]
    if len(names) != len(set(names)):
        problems.append("skill names must be unique across categories")
    return skills, problems


def load_agents(skill_names: set[str]) -> tuple[list[dict], list[str]]:
    problems: list[str] = []
    agents: list[dict] = []
    if not AGENTS_DIR.is_dir():
        raise SystemExit("agents/ is missing")
    for folder in sorted(path for path in AGENTS_DIR.iterdir() if path.is_dir()):
        manifest = folder / "AGENT.md"
        if not manifest.is_file():
            problems.append(f"{folder.relative_to(ROOT)} has no AGENT.md")
            continue
        text = manifest.read_text(encoding="utf-8")
        front = split_frontmatter(text)
        if not front.present or front.parse_error:
            problems.append(f"{manifest.relative_to(ROOT)} has unreadable frontmatter")
            continue
        name = field(front.fields, "name")
        if name != folder.name:
            problems.append(f"{manifest.relative_to(ROOT)} name must match the folder")
        description = field(front.fields, "description")
        added = field(front.fields, "added")
        if not description:
            problems.append(f"{name or folder.name} is missing a description")
        if not ISO_DATE.fullmatch(added):
            problems.append(f"{name or folder.name} added must be YYYY-MM-DD")
        bundled = split_list(field(front.fields, "skills"), comma=True)
        missing = [item for item in bundled if item not in skill_names]
        if missing:
            problems.append(f"{name} bundles unknown skills: {', '.join(missing)}")
        if not bundled:
            problems.append(f"{name} must bundle at least one skill")
        category = field(front.fields, "category")
        subshelf = field(front.fields, "subshelf")
        if not category or not subshelf:
            problems.append(f"{name or folder.name} needs category and subshelf")
        agents.append(
            {
                "name": name or folder.name,
                "description": description,
                "added": added,
                "category": category,
                "subshelf": subshelf,
                "skills": bundled,
                "connectors": split_list(field(front.fields, "connectors")),
                "prompts": split_list(field(front.fields, "prompts")),
                "body": front.body.strip() + "\n",
                "sourcePath": folder.relative_to(ROOT).as_posix(),
                **credit_fields(front.fields, nested=False),
            }
        )
    return agents, problems


def build(allow_findings: bool) -> dict:
    if RAW_DIR.exists():
        shutil.rmtree(RAW_DIR)
    RAW_DIR.mkdir(parents=True)
    skills, skill_problems = load_skills()
    agents, agent_problems = load_agents({item["name"] for item in skills})
    problems = skill_problems + agent_problems
    categories = load_shelves()
    by_id = {item["id"]: item for item in categories}
    for skill in skills:
        shelf = by_id.get(skill["category"])
        if shelf is None:
            problems.append(f"{skill['name']} is in an unknown shelf")
            continue
        sub = next((item for item in shelf["subshelves"] if item["slug"] == skill["subshelf"]), None)
        if sub is None:
            continue
        sub["skills"] = sub.get("skills", 0) + 1
    for agent in agents:
        shelf = by_id.get(agent.get("category"))
        if shelf is None:
            problems.append(f"{agent['name']} category is not a shelf")
            continue
        sub = next((item for item in shelf["subshelves"] if item["slug"] == agent.get("subshelf")), None)
        if sub is None:
            problems.append(f"{agent['name']} subshelf is not on {shelf['id']}")
            continue
        sub["agents"] = sub.get("agents", 0) + 1
        agent["categoryLabel"] = shelf["label"]
        agent["shelfNumber"] = shelf["number"]
        agent["subshelfLabel"] = sub["label"]
        agent["callNumber"] = f"{shelf['number']}.{sub['number']}"
    for shelf in categories:
        for sub in shelf["subshelves"]:
            sub["skills"] = sub.get("skills", 0)
            sub["agents"] = sub.get("agents", 0)
        shelf["count"] = sum(sub["skills"] for sub in shelf["subshelves"])
        shelf["agentCount"] = sum(sub["agents"] for sub in shelf["subshelves"])
    categories.sort(key=lambda item: item["number"])
    dates = sorted({item["added"] for item in skills} | {item["added"] for item in agents}, reverse=True)
    drops = []
    for day in dates:
        drops.append(
            {
                "date": day,
                "skills": [item["name"] for item in skills if item["added"] == day],
                "agents": [item["name"] for item in agents if item["added"] == day],
            }
        )
    errors = sum(item["lint"]["errors"] for item in skills)
    warnings = sum(item["lint"]["warnings"] for item in skills)
    info = sum(item["lint"]["info"] for item in skills)
    clean = sum(1 for item in skills if item["lint"]["badge"] == "clean")
    catalog = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "repoUrl": REPO_URL,
        "owner": {
            "name": "Brandon",
            "github": "https://github.com/brandononchain",
            "site": "https://brandononchain.com",
        },
        "specUrl": "https://agentskills.io/specification",
        "aaifUrl": "https://aaif.io/projects/agent-skills",
        "studyUrl": "https://arxiv.org/abs/2607.01456",
        "stats": {
            "skills": len(skills),
            "agents": len(agents),
            "categories": len(categories),
            "errors": errors,
            "warnings": warnings,
            "info": info,
            "clean": clean,
        },
        "scoring": SCORING,
        "rules": [
            {
                "group": group["group"],
                "rules": [
                    {"id": rule_id, "severity": severity, "summary": summary}
                    for rule_id, severity, summary in group["rules"]
                ],
            }
            for group in RULES
        ],
        "categories": categories,
        "skills": sorted(skills, key=lambda item: (item["added"], item["name"]), reverse=True),
        "agents": sorted(agents, key=lambda item: (item["added"], item["name"]), reverse=True),
        "drops": drops,
        "audit": attach_audits(skills, agents),
    }
    # Stable skill order for the site is newest first; name asc within a day.
    catalog["skills"] = sorted(skills, key=lambda item: item["name"])
    catalog["skills"].sort(key=lambda item: item["added"], reverse=True)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.write_text(json.dumps(catalog, indent=2) + "\n", encoding="utf-8")
    print(
        f"indexed {len(skills)} skills, {len(agents)} agents, "
        f"{errors} error(s), {warnings} warning(s), {info} info"
    )
    print(f"wrote {DATA_PATH.relative_to(ROOT)}")
    refresh_readme_counts(len(skills), len(agents))
    if problems or errors or warnings:
        for problem in problems:
            print(f"error: {problem}", file=sys.stderr)
        if not allow_findings:
            raise SystemExit(1)
    sys.path.insert(0, str(ROOT / "tools"))
    from certlib import publish_certificates

    certificates = publish_certificates(certification_entries(skills, agents))
    write_readme(catalog, certificates["stats"])
    return catalog


AUTHOR_LOGIN = "brandononchain"


def attach_audits(skills: list[dict], agents: list[dict]) -> dict:
    """Audit every entry, record first-seen dates, and return the catalog summary."""
    sys.path.insert(0, str(ROOT / "tools"))
    from audit.engine import audit_directory, catalog_meta, public_view
    from audit.grace import load_ledger, remember, save_ledger
    from certlib import content_digest, git_commit, today_iso

    ledger = load_ledger(ROOT)
    today = today_iso()
    views: list[dict] = []

    def one(entry_id: str, directory: Path) -> dict:
        findings, lock, cve = audit_directory(directory)
        remember(ledger, entry_id, findings, today)
        view = public_view(
            findings,
            lock=lock,
            content_digest=content_digest(directory),
            commit=git_commit(ROOT, directory),
            ledger=ledger,
            entry_id=entry_id,
            today=today,
            cve_lookup=cve,
        )
        views.append(view)
        return view

    for skill in skills:
        skill["audit"] = one(f"skill-{skill['name']}", ROOT / skill["sourcePath"])
    for agent in agents:
        agent["audit"] = one(f"agent-{agent['name']}", ROOT / agent["sourcePath"])
    save_ledger(ROOT, ledger)
    return catalog_meta(views)


def certification_entries(skills: list[dict], agents: list[dict]) -> list[dict]:
    scores = {item["name"]: item["lint"]["score"] for item in skills}
    entries = []
    for skill in skills:
        entries.append(
            {
                "kind": "skill",
                "name": skill["name"],
                "title": skill["title"],
                "source_path": skill["sourcePath"],
                "authorLogin": AUTHOR_LOGIN,
                "audit": skill.get("audit"),
                "lint": {
                    "score": skill["lint"]["score"],
                    "errors": skill["lint"]["errors"],
                    "warnings": skill["lint"]["warnings"],
                    "info": skill["lint"]["info"],
                    "gate": "skill-lint",
                    "summary": "skill-lint score. Listed requires 100.",
                },
            }
        )
    for agent in agents:
        missing = [name for name in agent["skills"] if scores.get(name) != 100]
        ok = not missing
        entries.append(
            {
                "kind": "agent",
                "name": agent["name"],
                "title": agent["name"],
                "source_path": agent["sourcePath"],
                "authorLogin": AUTHOR_LOGIN,
                "audit": agent.get("audit"),
                "lint": {
                    "score": 100 if ok else 0,
                    "errors": 0 if ok else len(missing) or 1,
                    "warnings": 0,
                    "info": 0,
                    "gate": "agent-manifest",
                    "summary": (
                        "Manifest accepted and every bundled skill scores 100."
                        if ok
                        else "Bundled skills below 100: " + ", ".join(missing)
                    ),
                },
            }
        )
    return entries


def refresh_readme_counts(skill_count: int, agent_count: int) -> None:
    """Keep the README shields in step with the catalog. The badges are generated."""
    path = ROOT / "README.md"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    updated = re.sub(r"(badge/skills-)\d+(_linted-)", rf"\g<1>{skill_count}\2", text, count=1)
    updated = re.sub(r"(badge/agents-)\d+(-)", rf"\g<1>{agent_count}\2", updated, count=1)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        print(f"updated README counts: {skill_count} skills, {agent_count} agents")


def shield(label: str, message: str, color: str, label_color: str, href: str) -> str:
    """Static shields.io badge. Dashes in the label or message are escaped."""

    def encode(value: str) -> str:
        return value.replace("-", "--").replace("_", "__").replace(" ", "_")

    url = f"https://img.shields.io/badge/{encode(label)}-{encode(message)}-{color}?style=flat-square&labelColor={label_color}"
    return f"[![{label}]({url})]({href})"


def site_origin() -> str:
    config_path = ROOT / "config" / "site.json"
    try:
        origin = json.loads(config_path.read_text(encoding="utf-8")).get("origin") or ""
    except (OSError, json.JSONDecodeError):
        origin = ""
    origin = str(origin).strip().rstrip("/")
    return origin or "https://agentpedia.sh"


def license_name() -> str:
    text = (ROOT / "LICENSE").read_text(encoding="utf-8")
    if "Apache License" in text and "Version 2.0" in text:
        return "Apache-2.0"
    raise SystemExit("LICENSE is not Apache-2.0; the README badge was not guessed")


def grade_phrase(grades: dict) -> str:
    order = ("A", "B", "C", "D", "F")
    return ", ".join(f"{int(grades.get(letter) or 0)} {letter}" for letter in order)


def lint_phrase(stats: dict) -> str:
    skills = int(stats["skills"])
    clean = int(stats["clean"])
    errors = int(stats["errors"])
    warnings = int(stats["warnings"])
    if clean == skills and errors == 0 and warnings == 0:
        return f"100 on all {skills} skills, 0 errors, 0 warnings"
    return f"{clean} of {skills} at 100, {errors} errors, {warnings} warnings"


def render_badges(catalog: dict, cert_stats: dict) -> str:
    stats = catalog["stats"]
    audit = catalog["audit"]["stats"]
    origin = site_origin()
    grades = audit["grades"]
    nonzero = [(letter, int(grades.get(letter) or 0)) for letter in ("A", "B", "C", "D", "F")]
    present = [pair for pair in nonzero if pair[1]]
    if len(present) == 1:
        audit_message = f"{present[0][1]} {present[0][0]}"
    else:
        audit_message = " ".join(f"{count}{letter}" for letter, count in nonzero)
    latest = catalog["drops"][0]["date"] if catalog.get("drops") else "none"
    repo = catalog["repoUrl"]
    paper = "f4efe4"
    ink = "10110e"
    accent = "0e4f57"
    warm = "efe6d2"
    alert = "ff5a36"
    muted = "c9c0ae"
    lint_color = accent if int(stats["errors"]) == 0 and int(stats["warnings"]) == 0 else alert
    hold = int(audit["onHold"])
    badges = [
        shield("skills", str(stats["skills"]), accent, paper, repo),
        shield("agents", str(stats["agents"]), warm, ink, repo),
        shield("shelves", str(stats["categories"]), accent, paper, f"{origin}/"),
        shield(
            "lint",
            "all 100, 0 errors" if int(stats["clean"]) == int(stats["skills"]) and int(stats["errors"]) == 0 and int(stats["warnings"]) == 0 else f"{stats['errors']} errors, {stats['warnings']} warnings",
            lint_color,
            paper,
            f"{origin}/lint",
        ),
        shield("audit", audit_message, accent, paper, f"{origin}/security"),
        shield("listed", str(cert_stats["listed"]), warm, ink, f"{origin}/certification"),
        shield("verified", str(cert_stats["verified"]), accent, paper, f"{origin}/certification"),
        shield("certified", str(cert_stats["certified"]), ink, paper, f"{origin}/certification"),
        shield("on hold", str(hold), alert if hold else muted, ink, f"{origin}/security"),
        shield("latest drop", latest, ink, paper, f"{origin}/changelog"),
        shield("license", license_name(), muted, ink, "LICENSE"),
        shield("site", "agentpedia.sh", accent, paper, origin),
    ]
    return "\n".join(badges)


def render_stats_table(catalog: dict, cert_stats: dict) -> str:
    stats = catalog["stats"]
    audit = catalog["audit"]["stats"]
    latest = catalog["drops"][0]["date"] if catalog.get("drops") else "Not recorded"
    rows = [
        ("Skills", str(stats["skills"])),
        ("Agents", str(stats["agents"])),
        ("Shelves", str(stats["categories"])),
        ("Lint", lint_phrase(stats)),
        ("Audit", grade_phrase(audit["grades"])),
        ("Listed", str(cert_stats["listed"])),
        ("Verified", str(cert_stats["verified"])),
        ("Certified", str(cert_stats["certified"])),
        ("On hold", str(audit["onHold"])),
        ("Latest drop", latest),
    ]
    lines = ["| | |", "| --- | --- |"]
    lines.extend(f"| {name} | {value} |" for name, value in rows)
    return "\n".join(lines)


def render_vetting(grace_days: int) -> str:
    return (
        "A skill is listed only when skill-lint scores 100 and the static audit is not on hold. "
        "The build fails on a lint error or a warning. The audit grades A through F. "
        f"A high finding inside its {grace_days}-day grace period is a warning and can still be listed. "
        "On hold means grade F, a critical finding, or a high finding past that grace period. "
        "Listed is that gate. Verified adds a recorded check run. Certified adds a named review. "
        "Phase 1 reads the files. It does not execute the entry."
    )


def replace_marked(text: str, name: str, body: str) -> str:
    start = f"<!-- {name}:start -->"
    end = f"<!-- {name}:end -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    block = f"{start}\n{body.rstrip()}\n{end}"
    if not pattern.search(text):
        raise SystemExit(f"README is missing {start} / {end}")
    return pattern.sub(lambda _match: block, text, count=1)


def write_readme(catalog: dict, cert_stats: dict) -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    text = replace_marked(text, "badges", render_badges(catalog, cert_stats))
    text = replace_marked(text, "stats", render_stats_table(catalog, cert_stats))
    grace_days = int(catalog["audit"]["graceDays"])
    text = replace_marked(text, "vetting", render_vetting(grace_days))
    path.write_text(text if text.endswith("\n") else text + "\n", encoding="utf-8")
    print(f"wrote {path.relative_to(ROOT)} badges and stats")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Agentpedia catalog JSON.")
    parser.add_argument(
        "--allow-findings",
        action="store_true",
        help="Write the index even when skills have errors or warnings.",
    )
    args = parser.parse_args()
    build(allow_findings=args.allow_findings)


if __name__ == "__main__":
    main()
