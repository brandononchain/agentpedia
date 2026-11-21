import { REPO_URL, SITE_ORIGIN } from "@/lib/site";

export const AGENT_PROMPT = `You are submitting one skill or one agent to Agentpedia (${REPO_URL}). Finish the submission. Do not force-push. Do not invent a lint score or an audit grade. Read ${SITE_ORIGIN}/submit.md and follow it.

1. Work on a branch or a fork. If the checkout is on the default branch, create a branch before committing.
2. Pick an existing shelf and sub-shelf. \`python3 tools/new_entry.py shelves\` lists shelves. A new shelf also needs --label, --blurb, --subshelf-label, and --subshelf-description.
3. Scaffold, lint, and audit with one command. For a skill:
   python3 tools/new_entry.py submit --kind skill --category <shelf> --subshelf <slug> --name <name> --description "<third person. Use when the user asks for this job.>"
   For an agent, pass --kind agent, --skills as a comma-separated list of skills that already exist, and the same --category and --subshelf.
4. If the folder already exists, the command leaves the files in place, then lints and audits them.
5. Replace the placeholder example with a real one. Run the command again. skill-lint must score 100: zero errors, zero warnings, and zero info findings. The static audit must be passed, or warning while the printed grace period remains. On hold means stop and fix the finding. Do not weaken a rule to get a clean result.
6. The command prints git and gh commands. It does not run them. Show those commands to the user and wait for confirmation before publishing the branch. Never use --force.
7. Open a pull request with the submission template. Say what the entry does, what it refuses, the lint score, and the audit grade the command printed.`;

export function submitMarkdown() {
  return `# Submit an entry to Agentpedia

This file is the machine-readable submission spec. Humans can use ${SITE_ORIGIN}/submit. An agent can follow the prompt below, or install \`skills/skill-authoring/agentpedia-submit/SKILL.md\`.

Repository: ${REPO_URL}

The local path does not use npx. It is Python 3 and the standard library.

## Entry format

A skill is a folder:

\`\`\`
skills/<shelf>/<name>/SKILL.md
skills/<shelf>/<name>/scripts/      optional
skills/<shelf>/<name>/references/   optional
skills/<shelf>/<name>/assets/       optional
\`\`\`

An agent is one file: \`agents/<name>/AGENT.md\`. It names skills that already exist. A skill belongs to one agent. Add a new skill's name to that agent's \`skills\` list.

\`<name>\` is lowercase, hyphenated, and matches the folder. \`<shelf>\` is an existing directory under \`skills/\` with a \`category.json\`, unless you are opening a new shelf.

## Required skill frontmatter

\`\`\`yaml
---
name: <name>
description: >-
  <Third person. What it does. Use when the user asks for this job.>
license: Apache-2.0
metadata:
  category: <shelf>
  subshelf: <slug already on that shelf>
  tags: <comma-separated words>
  added: "YYYY-MM-DD"
  featured: false
---
\`\`\`

The description is at least 40 characters, third person, and contains \`Use when\`. The body has a title, numbered steps, one realistic example, and a validation step. Relative links point at files that exist.

## Required agent frontmatter

\`\`\`yaml
---
name: <name>
description: >-
  <Third person. Use when the user wants this job.>
added: "YYYY-MM-DD"
category: <shelf>
subshelf: <slug>
skills: <comma-separated skill names>
connectors: none
prompts: <one prompt, or several separated by \` || \`>
---
\`\`\`

## Commands

Scaffold, lint, and audit a new skill. The command prints the pull-request steps. It does not push.

\`\`\`bash
python3 tools/new_entry.py submit --kind skill \\
  --category <shelf> \\
  --subshelf <slug> \\
  --name <name> \\
  --description "<Third person. Use when the user asks for this job.>"
\`\`\`

Same path for an agent:

\`\`\`bash
python3 tools/new_entry.py submit --kind agent \\
  --name <name> \\
  --category <shelf> \\
  --subshelf <slug> \\
  --description "<Third person. Use when the user wants this job.>" \\
  --skills <existing-skill>
\`\`\`

Run the checks on their own:

\`\`\`bash
PYTHONPATH=tools/skill-lint python3 -m skill_lint skills/<shelf>/<name>
PYTHONPATH=tools python3 -m audit --path skills/<shelf>/<name>
python3 tools/build_index.py
\`\`\`

Agents are not passed through skill-lint. \`build_index.py\` checks the manifest. The audit command accepts an agent directory too.

## Pull request

1. Create a branch if you are on the default branch.
2. Commit the entry. Do not commit secrets.
3. Publish the branch with \`git push -u origin HEAD\`.
4. Open a pull request and choose the submission template.

The scaffold command prints these steps. It does not run them. Do not force-push.

## Acceptance

- skill-lint score is 100. That means zero errors, zero warnings, and zero info findings.
- The static audit status is passed, or warning while a high finding is still inside its grace period.
- On hold (any critical finding, grade F, or a high finding past grace) is not listed. Fix the entry. Do not delete a rule to make it pass.
- The text is original. No credentials, no piped shell installs, and no machine-specific absolute paths.
- Listed also requires the catalog build. Verified adds a recorded harness run. Certified adds a named review, and the reviewer cannot be the recorded author.

Phase 1 reads the files. It does not execute the entry. Sandbox, red-team, and manual review are design hooks and are not gates yet.

## Prompt

Copy this into Cursor, Claude Code, Codex, or another coding agent:

\`\`\`
${AGENT_PROMPT}
\`\`\`
`;
}
