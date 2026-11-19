---
name: conventional-commit-check
description: >-
  Checks a commit message against Conventional Commits 1.0.0 and reports the
  type, the scope, and whether it is breaking. Use when the user asks if a
  message matches that spec before committing.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/check_commit.py. Reads one local message
  file. No network and no extra packages.
metadata:
  category: dev-tools
  subshelf: git
  tags: commits, conventional
  added: "2026-11-19"
  featured: false
---

# Conventional commit check

Judge one commit message against Conventional Commits 1.0.0. Use [scripts/check_commit.py](scripts/check_commit.py). Which tokens count as breaking, and what the script refuses to infer, is in [references/spec-rules.md](references/spec-rules.md).

## Steps

1. Take the message as a file. If the user has a diff and no message, stop. Drafting a message is git-commit-writer. Do not invent a type or a scope.
2. Run `python3 scripts/check_commit.py` on that file. The fixture is [assets/message.txt](assets/message.txt), and it is not the user's commit.
3. When `ok=yes`, report `type`, `scope`, `breaking`, `breaking_from`, `footers`, and each `footer_token` as printed. An empty `scope` means the subject had no parentheses.
4. When `ok=no`, stop and quote `reason`. `header` means the first line is not a type, an optional scope, an optional `!`, a colon, and a space. `blank-line` means text follows the subject without a blank line. `empty` means there was no message. Do not rewrite it unless they ask.
5. Check the printed type against the first line, and check `breaking=yes` against a `!` before the colon or a footer token the script listed. Drop a claim the output does not show.
6. Do not commit, amend, or choose the next version. A version from classified types is semver-bump-plan.

## Example

User: Does this message match Conventional Commits? It is saved as `assets/message.txt`. Do not commit, and do not pick a version.

Agent: Runs `python3 scripts/check_commit.py assets/message.txt`.

```
ok=yes
type=feat
scope=
breaking=yes
breaking_from=both
footers=1
footer_token=BREAKING CHANGE
```

The subject is `feat!` with no scope. The footer token is `BREAKING CHANGE`, so the break is marked in both places. The message is not rewritten, and no version is chosen.

## Boundaries

Do not treat a passing check as permission to commit. Do not apply a 50-character subject rule. Do not read a version number out of the type. `ok=yes` means the structure matches the rules in [references/spec-rules.md](references/spec-rules.md). It does not mean the type is the right word for the diff.
