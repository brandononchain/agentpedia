#!/usr/bin/env python3
"""Add one skill or agent dated today, lint it, and refresh the catalog.

Examples
--------
python3 tools/new_entry.py skill \\
  --category dev-tools \\
  --name retry-notes \\
  --description "Writes a retry policy from a handler. Use when the user asks how a call should retry." \\
  --tags retries, http

python3 tools/new_entry.py agent \\
  --name release-captain \\
  --description "Prepares a release note and a changelog from the branch. Use when the user wants a release workflow." \\
  --skills changelog-from-commits, release-notes-editor
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import textwrap
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "skill-lint"))

from skill_lint.rules import NAME_RE, UNCLEAR_NAMES  # noqa: E402

TODAY = date.today().isoformat()


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def wrapped_description(description: str) -> str:
    lines = textwrap.wrap(description.strip(), width=78) or [description.strip()]
    return "description: >-\n" + "\n".join(f"  {line}" for line in lines)


def skill_markdown(args: argparse.Namespace) -> str:
    title = args.name.replace("-", " ").capitalize()
    tags = ", ".join(part.strip() for part in args.tags.split(",") if part.strip()) or "draft"
    body = f"""# {title}

Say what finished work looks like, then the boundary this skill will not cross.

## Steps

1. Confirm the input and the output the user wants.
2. Do the work from the files and facts the user supplied. Do not invent missing facts.
3. Validate the result against a check you can point at, then show the work and wait.

## Example

User: Replace this with a realistic request before shipping the skill.

Agent: Show a short concrete result, then delete this placeholder sentence.
"""
    return "\n".join(
        [
            "---",
            f"name: {args.name}",
            wrapped_description(args.description),
            "license: Apache-2.0",
            "metadata:",
            f"  category: {args.category}",
            f"  tags: {tags}",
            f'  added: "{TODAY}"',
            "  featured: false",
            "---",
            "",
            body.rstrip(),
            "",
        ]
    )


def ensure_category(category: str, label: str | None, blurb: str | None) -> None:
    folder = ROOT / "skills" / category
    folder.mkdir(parents=True, exist_ok=True)
    meta = folder / "category.json"
    if meta.is_file():
        return
    if not label or not blurb:
        fail(f"new category {category} needs --label and --blurb")
    meta.write_text(
        json.dumps({"label": label, "blurb": blurb}, indent=2) + "\n",
        encoding="utf-8",
    )


def check_name(name: str) -> None:
    if not NAME_RE.fullmatch(name):
        fail("name must be lowercase letters, numbers, and single hyphens")
    if name.lower() in UNCLEAR_NAMES or len(name) < 3:
        fail(f"name '{name}' is too generic; say what the entry does")


def lint_skill_folder(folder: Path) -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "tools" / "skill-lint")
    completed = subprocess.run(
        [sys.executable, "-m", "skill_lint", "--json", str(folder)],
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=True,
    )
    try:
        payload = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError:
        print(completed.stdout)
        print(completed.stderr, file=sys.stderr)
        fail("skill-lint did not return JSON")
    findings = payload.get("findings") or []
    if findings or completed.returncode != 0:
        text = subprocess.run(
            [sys.executable, "-m", "skill_lint", str(folder)],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
        )
        print(text.stdout)
        fail("the new skill has lint findings; edit it, then run python3 tools/build_index.py")


def refresh_index() -> None:
    subprocess.check_call([sys.executable, str(ROOT / "tools" / "build_index.py")], cwd=ROOT)


def add_skill(args: argparse.Namespace) -> None:
    check_name(args.name)
    description = " ".join(args.description.split())
    if len(description) < 40:
        fail("description must be at least 40 characters and say when to use the skill")
    if "when" not in description.lower():
        fail("description must say when to use the skill (for example, 'Use when')")
    ensure_category(args.category, args.label, args.blurb)
    folder = ROOT / "skills" / args.category / args.name
    if folder.exists():
        fail(f"{folder.relative_to(ROOT)} already exists")
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(skill_markdown(args), encoding="utf-8")
    print(f"wrote {folder.relative_to(ROOT)}/SKILL.md")
    lint_skill_folder(folder)
    refresh_index()
    print(f"dated {TODAY}. Replace the example placeholder if it is still generic, then lint again.")


def add_agent(args: argparse.Namespace) -> None:
    check_name(args.name)
    description = " ".join(args.description.split())
    if len(description) < 40 or "when" not in description.lower():
        fail("description must be at least 40 characters and say when to use the agent")
    skills = [part.strip() for part in args.skills.split(",") if part.strip()]
    if not skills:
        fail("pass --skills as a comma-separated list of existing skill names")
    known = set()
    for path in (ROOT / "skills").glob("*/*/SKILL.md"):
        known.add(path.parent.name)
    missing = [name for name in skills if name not in known]
    if missing:
        fail("unknown skills: " + ", ".join(missing))
    folder = ROOT / "agents" / args.name
    if folder.exists():
        fail(f"{folder.relative_to(ROOT)} already exists")
    folder.mkdir(parents=True)
    connectors = args.connectors.strip() if args.connectors else "none"
    prompts = args.prompts.strip() if args.prompts else (
        f"Show me how you would use {skills[0]} on a realistic input. || "
        "Which bundled skill applies, and what will you refuse to do?"
    )
    title = args.name.replace("-", " ").capitalize()
    text = "\n".join(
        [
            "---",
            f"name: {args.name}",
            wrapped_description(description),
            f'added: "{TODAY}"',
            "skills: " + ", ".join(skills),
            "connectors: " + connectors,
            "prompts: " + prompts,
            "---",
            "",
            f"# {title}",
            "",
            "Say which skill you reach for first, and what you will not do even if asked.",
            "",
            "## Steps",
            "",
            "1. Pick the bundled skill that matches the request. If none matches, say so.",
            "2. Follow that skill. Do not skip its safety limits.",
            "3. Check the result against the skill's validation step before you hand it back.",
            "",
            "## Example",
            "",
            "User: Ask for the job this agent exists to do.",
            "",
            "Agent: Name the skill used and the limit that still applies.",
            "",
        ]
    )
    (folder / "AGENT.md").write_text(text, encoding="utf-8")
    print(f"wrote {folder.relative_to(ROOT)}/AGENT.md")
    refresh_index()
    print(f"dated {TODAY}. Edit the manifest, then run python3 tools/build_index.py.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Add an Agentpedia entry dated today.")
    sub = parser.add_subparsers(dest="kind", required=True)

    skill_parser = sub.add_parser("skill", help="Scaffold a skill and lint it")
    skill_parser.add_argument("--category", required=True)
    skill_parser.add_argument("--name", required=True)
    skill_parser.add_argument("--description", required=True)
    skill_parser.add_argument("--tags", default="draft")
    skill_parser.add_argument("--label", help="Shelf label, required only for a new category")
    skill_parser.add_argument("--blurb", help="Shelf sentence, required only for a new category")
    skill_parser.set_defaults(func=add_skill)

    agent_parser = sub.add_parser("agent", help="Scaffold an agent manifest")
    agent_parser.add_argument("--name", required=True)
    agent_parser.add_argument("--description", required=True)
    agent_parser.add_argument("--skills", required=True, help="Comma-separated skill names")
    agent_parser.add_argument("--connectors", default="none")
    agent_parser.add_argument(
        "--prompts",
        default="",
        help="Sample prompts separated by ' || '",
    )
    agent_parser.set_defaults(func=add_agent)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
