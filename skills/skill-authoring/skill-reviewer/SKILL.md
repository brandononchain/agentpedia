---
name: skill-reviewer
description: >-
  Reviews a SKILL.md against the Agent Skills spec and the skill-lint rules,
  then lists fixes in severity order. Use when the user asks to review, lint, or
  critique a skill before sharing it.
license: Apache-2.0
metadata:
  category: skill-authoring
  tags: skills, review, lint
  added: "2026-11-10"
  featured: false
---

# Skill reviewer

Review one skill folder. Report spec failures first, then smells, then safety. Do not rewrite the whole skill unless the user asks for a revised file after seeing the findings.

## Steps

1. Read `SKILL.md` and list the files next to it. Note missing targets for any relative link.
2. Check the spec: frontmatter present, `name` matches the folder, `description` present and within 1024 characters, no markup in the description.
3. Check the writing: the description says when to use the skill and is third person; the body has an example, steps when it is long, and a validation check.
4. Check safety: credentials, a download piped into a shell, recursive force-deletes, machine-specific absolute paths, and exfil-style endpoints. Describe the problem without repeating a live secret.
5. If skill-lint is available, run it and merge its findings with yours. Validate that every finding cites a line or a missing file. Order the list error, then warning, then note. End with ship, ship after fixes, or do not ship.

## Example

User: Review a skill whose description is "Helps with PDFs" and whose body has no example.

Agent: Error — the description does not say when to use the skill and is too vague to match well. Warning — the body has no example. Recommendation: do not ship. No rewritten file is produced until the user asks for one.

## Boundaries

Do not lower a safety finding to a style note. Do not add a secret to the review in order to illustrate one.
