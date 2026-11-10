---
name: pr-review-notes
description: >-
  Reviews a diff and writes findings ordered by severity, each with a file
  reference and a test note. Use when the user asks for a code review, a PR
  review, or a second pass before merge.
license: Apache-2.0
metadata:
  category: dev-tools
  tags: review, git
  added: "2026-11-08"
  featured: true
---

# PR review notes

Review the change the user points at. Lead with defects that can ship a bug, lose data, or weaken auth. Leave style nits out unless the user asked for them.

Read [the rubric](references/rubric.md) before writing findings.

## Steps

1. Read the diff and any description the user supplied. If the diff is missing, ask for it.
2. Walk the rubric: correctness, data loss, auth, concurrency, migrations, and tests.
3. Write findings first, ordered blocker, then should-fix, then note. Each finding names the file and the behavior, not a vague worry.
4. Add a short test note: what was covered, and which behavior is still untested.
5. Validate that every finding is visible in the diff. Delete any comment about code that did not change. End with a one-line merge recommendation: ready, ready after the blockers, or not ready.

## Example

User: Review the diff that adds a `deleted_at` filter to the invoice query.

Agent: Blocker — `src/invoices/list.ts` applies `deleted_at is null` in the list query but not in the CSV export, so a deleted invoice can still be exported. Should-fix — the new filter has no test for a row whose `deleted_at` is in the future. Recommendation: not ready.

## Boundaries

Do not rewrite the change. Do not approve a diff you have not seen.
