---
name: semver-bump-plan
description: >-
  Chooses the highest SemVer bump from commit types the user already classified,
  using the Conventional Commits correlation. Use when the user asks whether the
  next release is major, minor, patch, or none.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/plan_bump.py. Reads a local text file. No
  network and no extra packages.
metadata:
  category: dev-tools
  subshelf: git
  tags: semver, release
  added: "2026-11-19"
  featured: false
---

# SemVer bump plan

Choose one bump from commit types the user has already classified. Use [scripts/plan_bump.py](scripts/plan_bump.py). The correlation and the cases where the next number is not computed are in [references/bump-rules.md](references/bump-rules.md).

## Steps

1. Take one line per commit: the type, then the word `breaking` only when that commit is breaking. If they handed you raw messages, stop and use conventional-commit-check. Copy `type` from that output, and add `breaking` only when it printed `breaking=yes`. Do not guess a type from a diff.
2. Take the current version only if they named one. Do not open a manifest to invent it. A missing version means the report stops at `bump`.
3. Run `python3 scripts/plan_bump.py` with `--types`. Add `--current` only for the version they named. The fixture is [assets/types.txt](assets/types.txt).
4. Report every `line`, then `commits`, the four counts, and `bump`. When a current version was passed, also report `prerelease`, `initial_development`, `build` if it is printed, and `next`.
5. Check each `class` against that line. A line with `breaking` is major even when the type is `feat` or `fix`. The highest class is `bump`. Quote `next=not-computed` instead of filling in a number.
6. Do not tag, publish, or edit a version field.

## Example

User: These lines are in `assets/types.txt`. The current version is `1.4.2`. What is the bump? Do not tag.

Agent: Runs `python3 scripts/plan_bump.py --types assets/types.txt --current 1.4.2`.

```
line=1 type=feat breaking=no class=minor
line=2 type=fix breaking=no class=patch
line=3 type=docs breaking=no class=none
line=4 type=chore breaking=yes class=major
commits=4
major=1
minor=1
patch=1
none=1
bump=major
current=1.4.2
prerelease=no
initial_development=no
next=2.0.0
```

The `chore` line is breaking, so it outranks the `feat`. `docs` adds nothing. `next` is `2.0.0` because the current major is greater than zero and there is no pre-release. Nothing is tagged.

## Boundaries

Do not parse a raw commit message in this skill. Do not treat major zero, a pre-release, or a leading `v` as a normal stable bump. `next=unchanged` means these lines do not call for a new number. It is not a release.
