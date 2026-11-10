---
name: diff-risk-scan
description: >-
  Flags risk in a diff across auth, data loss, migrations, money, concurrency,
  and silent behavior changes. Use when the user asks what could break, what is
  risky, or what to look at before merging.
license: Apache-2.0
metadata:
  category: dev-tools
  tags: review, risk
  added: "2026-11-08"
  featured: false
---

# Diff risk scan

Scan a diff for risk, not for style. A quiet change to a permission check outranks a large rename.

## Steps

1. Read the full diff. Group hunks by subsystem instead of reading top to bottom only.
2. Flag a hunk when it touches authentication, authorization, deletes, migrations, payments, retries, or shared mutable state.
3. Separately flag silent behavior changes: a new default, a wider query, a removed error, or a catch that swallows a failure.
4. For each flag, write the file, the behavior that changed, who is affected, and whether a rollback is easy.
5. Validate the scan by rereading flags against the diff. Remove anything you cannot point at. If nothing is risky, say that explicitly and name what you checked.

## Example

User: Scan this billing diff before I merge.

Agent: Risk — `billing/charge.ts` now treats a missing tax region as zero tax instead of failing the invoice. Customers in an unmapped region would be undercharged, and the old error was the only signal. Rollback is a revert; there is no migration. No auth or delete hunks in this diff.

## Boundaries

Do not claim a diff is safe because it is small. Do not propose exploit steps. Describe the user-visible failure.
