---
name: agentpedia-submit
description: >-
  Submits one skill or one agent to the Agentpedia catalog. It scaffolds the
  folder, runs skill-lint and the static audit, and prints the pull-request
  commands. Use when the user wants to add an entry to Agentpedia.
license: Apache-2.0
metadata:
  category: skill-authoring
  subshelf: writing
  tags: skills, submit
  added: "2026-11-21"
  featured: false
---

# Agentpedia submit

Add one original entry to an Agentpedia checkout. The spec is `https://agentpedia.sh/submit.md`. The command below scaffolds, lints, audits, and prints the publish steps. It does not publish the branch.

## Steps

1. Confirm whether the entry is a skill or an agent, the shelf, the sub-shelf, and the hyphenated name. List shelves with `python3 tools/new_entry.py shelves` from the checkout.
2. Run `python3 tools/new_entry.py submit` with `--kind skill` or `--kind agent`, plus `--category`, `--subshelf`, `--name`, and a third-person `--description` that says when to use the entry. An agent also needs `--skills` naming skills that already exist.
3. If the folder already exists, leave the files in place. Replace a placeholder example with a real one. Run the same command again.
4. Read the skill-lint score and the audit status the command prints. A skill is ready only at score 100. The audit must be passed, or a warning that still names days left. On hold means stop and fix the finding the report names.
5. Show the printed commands and wait for the user to confirm before publishing the branch. Do not force-push. Do not invent a score.

## Example

User: Add a skill named retry-notes on the dev-tools shelf, sub-shelf notes, that writes a retry policy from a handler the user pastes.

Agent: Runs `python3 tools/new_entry.py submit --kind skill --category dev-tools --subshelf notes --name retry-notes` with a description that says when to use it. The report shows skill-lint 100 and audit grade A, status passed. The agent shows the printed commit and pull-request commands and waits.

## Boundaries

Do not copy another author's skill text. Do not put a credential in the example. Do not weaken a lint or audit rule to get a clean result. Do not force-push.
