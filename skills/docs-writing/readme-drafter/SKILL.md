---
name: readme-drafter
description: >-
  Drafts a README that says what the project is, how to run it, and how to test
  it. Use when the user asks for a README or to rewrite one that does not
  explain how to start.
license: Apache-2.0
metadata:
  category: docs-writing
  tags: readme, docs
  added: "2026-11-07"
  featured: false
---

# README drafter

Write a README a new contributor can follow without asking someone. Use the project's real commands. If a command is unknown, leave a visible gap instead of inventing one.

## Steps

1. Read the project files the user pointed at: the manifest, the existing README, and any run script. Ask which package manager or runtime if it is ambiguous.
2. Open with one paragraph: what it is, who it is for, and what it is not.
3. Document prerequisites, install, the command that runs it locally, and the command that runs tests.
4. Add configuration only for variables a newcomer must set. Point at a sample env file if one exists. Never paste secret values.
5. Validate the draft by checking that every command appears in the project (a script, a documented tool, or a file the user named). Remove any step you cannot tie to the repo.

## Example

User: Draft a README for a Python CLI called `skill-lint` that runs with `python3 -m skill_lint` and tests with `python3 -m pytest`.

Agent: The first paragraph says it lints `SKILL.md` files. The run section shows `python3 -m skill_lint <path>` from a checkout. The test section shows `python3 -m pytest`. No install of unrelated tools is added.

## Boundaries

Do not describe features the code does not have. Do not add badges you have not generated.
