---
name: git-commit-writer
description: >-
  Drafts a Conventional Commits message from a diff and a one-line intent. Use
  when the user asks for a commit message or to summarize a change before
  committing.
license: Apache-2.0
metadata:
  category: dev-tools
  subshelf: git
  tags: git, commits
  added: "2026-11-09"
  featured: true
---

# Git commit writer

Draft a Conventional Commits message from the diff the user already has. Do not stage, commit, or push unless the user explicitly asks for that exact action after accepting the wording.

## Steps

1. Read the diff and status the user provided. If neither is present, ask for them. Do not invent files or ticket ids.
2. Pick a type (`feat`, `fix`, `docs`, `refactor`, `test`, `chore`, or `perf`) and a scope only when one module dominates the change.
3. Write an imperative subject of 50 characters or fewer, with no trailing period.
4. Add a body only when the reason is not obvious. Wrap near 72 characters and explain why, not a file list.
5. Validate the draft: one subject line, a blank line before any body, and no path the diff does not contain. Show the draft and wait.

## Example

User: Write a commit for a diff that retries webhook deliveries after a 429.

Agent:

```
fix(webhooks): retry deliveries that receive a 429

The client dropped the first rate-limit response. Retry three
times with backoff and store the last status on the delivery.
```

## Boundaries

Do not amend, rebase, or push. If the diff contains a credential, stop and tell the user to remove it before any commit.
