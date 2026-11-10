# Contributing to Skilldex

Skilldex publishes skills that an agent can follow and that a reviewer can check. A pull request that adds an entry should leave the linter at zero errors and zero warnings. Info findings are allowed, but the seed catalog has none, and a new entry should aim for the same.

## Add a skill

From the repo root:

```bash
python3 tools/new_entry.py skill \
  --category dev-tools \
  --name retry-notes \
  --description "Writes a retry policy from a handler. Use when the user asks how a call should retry." \
  --tags retries, http
```

That writes `skills/dev-tools/retry-notes/SKILL.md`, dated today, runs skill-lint, and rebuilds `data/catalog.json`.

If the category does not exist yet, pass `--label` and `--blurb` as well. Those land in `skills/<category>/category.json` and become the shelf name on the site.

Then replace the placeholder example with a real one. The scaffold is only a passing skeleton.

Check the folder again before you push:

```bash
PYTHONPATH=tools/skill-lint python3 -m skill_lint skills/dev-tools/retry-notes
python3 tools/build_index.py
```

`build_index.py` exits with status 1 when any skill has an error or a warning. `npm run build` runs that step, and so does CI.

## Add an agent

Agents are bundles, not a second kind of skill. They live in `agents/<name>/AGENT.md` and are not passed through skill-lint. The index build still checks that the name matches the folder, the date is `YYYY-MM-DD`, the description says when to use the agent, and every bundled skill exists.

```bash
python3 tools/new_entry.py agent \
  --name release-captain \
  --description "Prepares a changelog and release notes for a branch. Use when the user wants a release workflow." \
  --skills changelog-from-commits, release-notes-editor \
  --connectors "git on the local repository" \
  --prompts "Draft the changelog. Do not tag a release. || Rewrite the notes for end users."
```

Separate connectors and prompts with ` || ` when a value itself contains a comma.

## The quality bar

A skill is a folder. `name` matches the folder. The description is third person, says what the skill does, and says when to use it (`Use when …` is the phrase the linter looks for). The body has numbered steps, one realistic example, and a way to validate the result.

Put long reference material in `references/` and repeated commands in `scripts/`. Relative links must point at files that exist. Paths use forward slashes.

Do not put any of the following in a skill, including inside an example:

- A credential, token, or private key. Tell the agent to read a secret from the environment.
- A download piped into a shell.
- A recursive force-delete.
- A machine-specific absolute path.
- A webhook, tunnel, or paste-site URL.

Write original instructions. Do not paste someone else's skill verbatim.

Trading and market skills in this catalog record, size, and brief. They do not place orders and they do not invent prices. Match that restraint if you add to the shelf. Marketing and sales skills do not invent social proof, personal facts, or a feature the product does not have.

## What the site shows

`tools/build_index.py` is the only step between the folders and the website. It writes:

- `data/catalog.json` — what the Next.js pages render
- `public/raw/skills/...` — raw files
- `public/raw/zips/<name>.zip` — a download of the skill folder

The score starts at 100. An error costs 25, a warning costs 8, an info finding costs 2. The badge is `clean` only when errors and warnings are both zero. This catalog refuses to build otherwise.

## Linter tests

The linter is vendored at `tools/skill-lint` and has no runtime dependencies.

```bash
python3 -m pip install pytest
PYTHONPATH=tools/skill-lint python3 -m pytest tools/skill-lint/tests -q
```

Change the linter only when you mean to change the rules, and keep those tests passing. The rule list on the "How we lint" page is generated from `tools/build_index.py`, so update that table in the same change.
