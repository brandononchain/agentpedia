---
name: example-skill
description: >-
  Copies this template into a new skill folder and fills the steps, example, and
  boundaries. Use when the user asks for a starting SKILL.md that will pass
  skill-lint.
license: Apache-2.0
metadata:
  category: skill-authoring
  tags: template, submission
  added: "2026-11-10"
  featured: false
---

# Example skill

This folder is a template for a pull request. It is not a published Agentpedia entry. Copy it, replace the steps with the procedure you want an agent to follow, and keep the description in third person with a “Use when” line.

## Steps

1. Copy `submissions/template/example-skill/` to `skills/<category>/<name>/` or to `submissions/incoming/<name>/`.
2. Set `name` to the folder name. Keep `name` lowercase with hyphens.
3. Write the description as what the skill does and when to use it. Stay in third person.
4. Replace these steps with the real procedure. Name the inputs and the checks the agent should run.
5. Replace the example with a user request and the agent’s response, including the command or the file the agent would use.
6. Run `PYTHONPATH=tools/skill-lint python3 -m skill_lint` on the new folder. Fix every error and warning before opening the pull request.

## Example

User: Start a skill called `retry-notes` for writing a retry policy.

Agent: Copies this template to `submissions/incoming/retry-notes/`, sets `name: retry-notes`, and replaces the steps with the retry procedure the user described. The agent then runs skill-lint on that folder and reports the score.

## Boundaries

Do not publish this template as if it were the user’s skill. Do not invent a lint score. Say when the folder has not been linted yet.
