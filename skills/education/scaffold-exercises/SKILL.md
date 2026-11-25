---
name: scaffold-exercises
description: >-
  Scaffolds a course section into numbered exercise folders with a problem, a
  solution, or an explainer stub. Use when the user asks to scaffold exercises,
  stub a course section, or lay out practice problems before writing them.
license: MIT
metadata:
  category: education
  subshelf: practice
  tags: scaffold, exercises, education
  added: "2026-11-25"
  featured: false
  source: import
  author: Matt Pocock
  authorUrl: "https://github.com/mattpocock"
  authorKind: person
  curator: Brandon
  upstream: mattpocock/skills
  upstreamCommit: 6f7f7831a625f040a8e06a0e7954826b87ce775a
  upstreamPath: skills/misc/scaffold-exercises/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2026 Matt Pocock
---

# Scaffold exercises

Do this one job: a folder plan for practice exercises. Adapted from `mattpocock/skills` at commit `6f7f7831a625` (MIT). Copyright (c) 2026 Matt Pocock

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. Read the plan and list each section name, each exercise name, and which variant the user asked for: problem, solution, explainer, or more than one.
3. Number sections as `01-section-name` and exercises as `01.03-exercise-name`, using the order the user gave. Do not invent a section that was not in the plan.
4. For each variant, show a stub readme that has a title and one sentence from the plan. Leave the body blank when the plan has no sentence yet.
5. Show the tree. Create the directories only if the user asked for files on disk. Do not commit, and do not run a linter the user did not name.
6. If the user named a linter, run that command and list the failures. Do not install a package to get a linter.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Section "retrieval", then two exercises: "bm25" (problem and solution) and "citations" (explainer only). Do not invent learning goals.

Agent: A tree with `01-retrieval/01.01-bm25/problem`, `01-retrieval/01.01-bm25/solution`, and `01-retrieval/01.02-citations/explainer`, each with a one-line readme, and no goals beyond those names.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
