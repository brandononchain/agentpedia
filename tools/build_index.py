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


def read_category(folder: Path) -> tuple[str, str]:
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
    return label, blurb


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


def load_skills() -> tuple[list[dict], list[str]]:
    problems: list[str] = []
    skills: list[dict] = []
    if not SKILLS_DIR.is_dir():
        raise SystemExit("skills/ is missing")
    for category_dir in sorted(path for path in SKILLS_DIR.iterdir() if path.is_dir()):
        label, blurb = read_category(category_dir)
        category = category_dir.name
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
                    "tags": split_list(meta_value(front.fields, "tags"), comma=True),
                    "added": added,
                    "featured": meta_value(front.fields, "featured").lower() == "true",
                    "license": field(front.fields, "license") or "Apache-2.0",
                    "compatibility": field(front.fields, "compatibility"),
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
        agents.append(
            {
                "name": name or folder.name,
                "description": description,
                "added": added,
                "skills": bundled,
                "connectors": split_list(field(front.fields, "connectors")),
                "prompts": split_list(field(front.fields, "prompts")),
                "body": front.body.strip() + "\n",
                "sourcePath": folder.relative_to(ROOT).as_posix(),
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
    categories = []
    for category in sorted({item["category"] for item in skills}):
        sample = next(item for item in skills if item["category"] == category)
        count = sum(1 for item in skills if item["category"] == category)
        categories.append(
            {
                "id": category,
                "label": sample["categoryLabel"],
                "blurb": sample["categoryBlurb"],
                "count": count,
            }
        )
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
    if problems or errors or warnings:
        for problem in problems:
            print(f"error: {problem}", file=sys.stderr)
        if not allow_findings:
            raise SystemExit(1)
    return catalog


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
