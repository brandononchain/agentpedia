---
name: skill-author
description: >-
  Writes a new Agent Skill folder and checks it with skill-lint before calling
  it done. Use when the user asks to create, draft, or scaffold a SKILL.md file.
license: Apache-2.0
compatibility: >-
  skill-lint on Python 3.10 or newer when the Agentpedia checkout is present. The
  scaffold script uses only the standard library.
metadata:
  category: skill-authoring
  tags: skills, lint
  added: "2026-11-10"
  featured: true
---

# Skill author

Create one skill that passes skill-lint with no errors and no warnings. Follow [references/quality-bar.md](references/quality-bar.md). Use [scripts/scaffold_skill.py](scripts/scaffold_skill.py) when a Agentpedia checkout is available; otherwise write the same files by hand.

## Steps

1. Choose a lowercase hyphenated name that matches the folder and says what the skill does. Reject generic names such as helper, misc, or skill.
2. Write a third-person description that states the task and when to use it, including a phrase like "Use when". Keep it under 1024 characters and free of markup.
3. Write the body: what to do, numbered steps, one realistic example, and a validation check. Point long reference material at `references/` and repeated commands at `scripts/`.
4. Keep secrets, machine-specific absolute paths, and piped shell installs out of the file. Use relative paths that exist.
5. Run skill-lint on the folder (`PYTHONPATH=tools/skill-lint python3 -m skill_lint <folder>` from a Agentpedia checkout, or the project's linter). Validate that the report has zero errors and zero warnings. Fix the file and run it again before showing the skill as done.

## Example

User: Add a skill that turns commit subjects into a changelog.

Agent: Creates `skills/dev-tools/changelog-from-commits/SKILL.md` with a description that says when to use it, five numbered steps, an example with three subjects, and a check that every line maps to a commit. The lint report shows zero errors and zero warnings. The skill is shown only after that report.

## Boundaries

Do not ship a skill that still has lint errors. Do not copy a third-party skill in verbatim. Do not add credentials to the example.
