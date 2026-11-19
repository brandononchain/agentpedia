---
name: codeowners-match
description: >-
  Names the last CODEOWNERS pattern that matches each path the user lists, and
  the owners on that line. Use when the user asks who owns a file or which
  review rule would apply.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/match_owners.py. Reads two local files. No
  network and no extra packages.
metadata:
  category: dev-tools
  subshelf: review
  tags: review, codeowners
  added: "2026-11-19"
  featured: false
---

# CODEOWNERS match

Name the last matching CODEOWNERS rule for each path. Use [scripts/match_owners.py](scripts/match_owners.py). Which patterns match, which lines are skipped, and why a later line wins is in [references/pattern-rules.md](references/pattern-rules.md).

## Steps

1. Take one CODEOWNERS file. If `.github/CODEOWNERS`, a root `CODEOWNERS`, and `docs/CODEOWNERS` are all in play, GitHub uses the first of those three that exists, in that order. Do not merge them. If the user did not say which file that is, ask.
2. Take the paths, one repo-relative path per line. If a path is missing, ask. Do not run git, and do not invent a path from a diff they did not paste.
3. Run `python3 scripts/match_owners.py` with `--codeowners` and `--paths`. The fixtures are [assets/CODEOWNERS](assets/CODEOWNERS) and [assets/paths.txt](assets/paths.txt).
4. For each path, keep `matched`, and when it is `yes` keep `line`, `pattern`, `owners`, and `owners_empty`. Keep every `skip` line. If the script stops because the file is at least 3000000 bytes, say so and do not match a prefix.
5. Check a printed pattern against that line of the file. Drop a path whose pattern is not on that line. `owners_empty=yes` is a match that names nobody. It is not the same as `matched=no`.
6. Do not request a review, and do not claim an owner has write access.

## Example

User: Who matches the paths in `assets/paths.txt` under `assets/CODEOWNERS`? Do not open a pull request.

Agent: Runs `python3 scripts/match_owners.py --codeowners assets/CODEOWNERS --paths assets/paths.txt`.

```
path=src/app.js
matched=yes
line=7
pattern=*.js
owners=@js-owner
owners_empty=no
path=docs/getting-started.md
matched=yes
line=6
pattern=/docs/
owners=@docs-owner
owners_empty=no
path=docs/build-app/troubleshooting.md
matched=yes
line=6
pattern=/docs/
owners=@docs-owner
owners_empty=no
path=README.md
matched=yes
line=2
pattern=*
owners=@platform
owners_empty=no
paths=4
skipped=0
```

`src/app.js` hits `*.js` on line 7, which is later than the `*` on line 2. `docs/getting-started.md` also fits `docs/*` on line 4, and the later `/docs/` on line 6 wins. The nested docs path does not fit `docs/*`. `README.md` stays with `*`. No review is requested.

## Boundaries

Do not edit the CODEOWNERS file unless they ask. Do not treat a skipped negation or a character range as a match. A result is about this file and these paths, not about branch protection.
