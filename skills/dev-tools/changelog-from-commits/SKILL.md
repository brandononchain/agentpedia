---
name: changelog-from-commits
description: >-
  Turns commit subjects into a Keep a Changelog entry grouped by Added, Changed,
  Fixed, and Security. Use when the user asks for a changelog or a release
  section from git history.
license: Apache-2.0
metadata:
  category: dev-tools
  subshelf: git
  tags: changelog, git
  added: "2026-11-08"
  featured: false
---

# Changelog from commits

Write a changelog fragment from commit subjects the user provides. Follow Keep a Changelog: people-facing notes, grouped, newest section on top. Do not dump raw subjects.

## Steps

1. Read the commit list and the version or date the user wants. Ask for the range if it is ambiguous.
2. Drop merge commits, typo-only subjects, and chores that do not affect anyone using the product.
3. Group the rest under Added, Changed, Fixed, or Security. Rewrite each line so a user can tell what changed, without internal ticket slang.
4. Put breaking changes first inside Changed and start those lines with "Breaking:".
5. Validate that every kept line maps to a commit you were given, and that no line mentions a change that is not in the list. Show the fragment.

## Example

User: Changelog for these subjects: `feat: add CSV export`, `fix: honor deleted_at in export`, `chore: bump lint`.

Agent:

```
## Unreleased

### Added
- CSV export for the invoice list.

### Fixed
- The invoice export now skips rows that have been deleted.
```

The lint bump is omitted because it does not change product behavior.

## Boundaries

Do not invent a feature to make the section look fuller. Security fixes stay in Security even if the subject said `fix`.
