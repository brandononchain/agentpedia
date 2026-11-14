---
name: agents-md-writer
description: >-
  Drafts or refreshes AGENTS.md from the repository structure, the build and
  test commands, and the conventions the files already state. Use when the user
  asks for an agent guide for a repo. It does not invent a command the repo
  does not show.
license: Apache-2.0
metadata:
  category: dev-tools
  subshelf: guides
  tags: docs, agents
  added: "2026-11-11"
  featured: false
---

# AGENTS.md writer

Write a draft of `AGENTS.md` from the checkout the user has open. The section list is in [references/sections.md](references/sections.md). Do not commit the file unless the user asks after reading the draft.

## Steps

1. If an `AGENTS.md` already exists, treat the task as a refresh. Keep a rule that is still true. Replace a command that the manifest no longer contains, and say which file changed it.
2. Read the top-level tree, the README, and the package or build manifest. Record install, build, test, and lint only when a file shows the command. A missing command is "not found", not a guess.
3. Draft the five sections: purpose, layout, commands, conventions, boundaries. Layout names only directories that exist. Conventions quote or paraphrase a contributing file, a linter config, or a rule the user stated.
4. Check the draft. Every command must appear in a file you can name. Every directory must exist in the tree. Remove a path or a flag you did not see.
5. Show the draft and wait. Do not write it over the existing file until the user accepts it.

## Example

User: The README says `npm test` runs the unit tests. The tree has `src/` and `tools/`. There is no AGENTS.md. Do not commit.

Agent: Purpose is taken from the README's first sentence. Layout lists `src/` and `tools/`. Commands include `npm test` and mark install, build, and lint as not found, because those strings were not in the files. The draft is shown and not written to disk.

## Boundaries

Do not invent a test runner, a deploy step, or a code style the repo does not state. Do not commit, push, or delete an existing guide.
