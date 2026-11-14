---
name: docs-to-skill
description: >-
  Turns a README, an API docs page, or CLI help text into a draft SKILL.md with
  a when-to-use description, steps, and long material moved into references/.
  Use when the user wants to package an existing tool or library as an agent
  skill from docs they already have.
license: Apache-2.0
metadata:
  category: skill-authoring
  subshelf: writing
  tags: skills, docs
  added: "2026-11-10"
  featured: false
---

# Docs to skill

Package a tool or library the user already has docs for. The source is a README, one API docs page, or CLI help text. The result is a draft skill an agent can run, not a second copy of the docs.

This is not skill-author. That skill writes from a task the user describes. This one starts from source text and may not invent behavior the source does not state.

## Inputs

- The source itself: a file path in the repo, pasted help text, or one docs page. If more than one source is offered, use only the ones the user names.
- The job the skill should cover, if the source describes several. Ask when it is ambiguous.
- Any limit the user states (no network, no writes, no publishing).

## Outputs

- A `SKILL.md` draft: third-person description that says when to use it, numbered steps, one example, and a validation check.
- A `references/` file when the source has a long flag table, endpoint list, or sample payload. The body links to it and stays the short entrypoint.
- A short note of what the source did not say, so the gap is visible.

## Steps

1. Read only the source the user supplied. If it is missing, ask for it. Do not fetch a different version and mix it in without saying so.
2. Extract the job, how to invoke it, the required inputs, and the failures the source actually names. Use [the split](references/source-split.md) to decide what stays in the body and what moves to `references/`.
3. Write the description in third person. Include a "Use when" clause and the words a host would match: the tool name and the verb (profile, deploy, query).
4. Write numbered steps an agent can follow on every run. Point long tables at a references file instead of pasting them.
5. Add one example taken from the source. If the source has no example, write a short one and label it "constructed from the documented inputs," not as a real session.
6. Validate the draft against the source. Every command, flag, and endpoint in the draft must appear in the source. Every relative link must exist. Secrets from sample docs must be removed. If skill-lint is available, run it and show the report. Do not call the draft done without that check when the linter is present.

## Example

User: Package this help text. The tool profiles a CSV and prints the row count, empty cells, and a few sample values. It does not upload the file and it does not compute averages.

Agent: The draft description says the skill profiles a CSV and to use it when the user asks what is in an export before analysis. The steps say to run the documented profiler and to report only the counts it prints. No references file is added, because the help text is shorter than a flag table. The note says averages are outside the tool. The draft is shown with the lint report when skill-lint is available, and without a claim of a clean lint when it is not.

## Guardrails

Do not copy a third-party skill in verbatim. Do not promote sample credentials from the docs into the skill. Do not describe a flag, endpoint, or guarantee the source does not mention. Do not pipe an installer into a shell as a setup step.
