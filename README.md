# Skilldex

[![skills](https://img.shields.io/badge/skills-36_linted-d6f25c?style=flat-square&labelColor=10110e)](https://github.com/brandononchain/skilldex)
[![agents](https://img.shields.io/badge/agents-8-efe6d2?style=flat-square&labelColor=10110e)](https://github.com/brandononchain/skilldex)
[![lint errors](https://img.shields.io/badge/lint_errors-0-ff5a36?style=flat-square&labelColor=10110e)](https://github.com/brandononchain/skilldex/actions)
[![license](https://img.shields.io/badge/license-Apache--2.0-c9c0ae?style=flat-square&labelColor=10110e)](LICENSE)

Skilldex is an open directory of [Agent Skills](https://agentskills.io/specification) and the agents that bundle them. The format is now a project of the [Agentic AI Foundation](https://aaif.io/projects/agent-skills) at the Linux Foundation.

Most published skills do not meet their own authoring rules. In [From Anatomy to Smells](https://arxiv.org/abs/2607.01456), Hong, Imani, and Ahmed at UC Irvine studied 238 real `SKILL.md` files. 237 of them — over 99 percent — had at least one skill smell, and those smells rarely got fixed later.

Skilldex is the other way around. **Every entry is linted and safety-checked before it ships.** The site shows the score. The build fails if a skill has an error or a warning.

Maintained by [Brandon](https://brandononchain.com) ([github.com/brandononchain](https://github.com/brandononchain)).

## Run it

Python 3.10+ and Node 22.

```bash
npm install
npm run dev
```

The dev server prints a local URL on port **43123**. `npm run dev` rebuilds `data/catalog.json` from `skills/` and `agents/` before Next.js starts.

```bash
npm run build         # lint the catalog, write the index, then next build
npm run test:lint     # skill-lint unit tests
npm run lint:skills
```

## Layout

```
skills/<category>/<skill-name>/SKILL.md   # plus scripts/, references/, assets/
agents/<agent-name>/AGENT.md              # purpose, bundled skills, connectors, prompts
tools/skill-lint/                          # vendored dependency-free linter
tools/build_index.py                       # lints everything and writes data/catalog.json
tools/new_entry.py                         # one command to add today's skill or agent
src/                                       # Next.js App Router site
```

The index carries the name, description, category, tags, lint score and findings, file tree, and install snippets for Claude Code, Codex, Cursor, and Grok Bot. The site is generated from that JSON.

## Add a daily entry

One command scaffolds a dated folder, lints it, and refreshes the index:

```bash
python3 tools/new_entry.py skill \
  --category dev-tools \
  --name retry-notes \
  --description "Writes a retry policy from a handler. Use when the user asks how a call should retry." \
  --tags retries, http
```

```bash
python3 tools/new_entry.py agent \
  --name release-captain \
  --description "Prepares a changelog and release notes for a branch. Use when the user wants a release workflow." \
  --skills changelog-from-commits, release-notes-editor
```

A new category also needs `--label` and `--blurb` the first time. Then edit the placeholder example, and run:

```bash
PYTHONPATH=tools/skill-lint python3 -m skill_lint skills/<category>/<name>
python3 tools/build_index.py
```

The quality bar, and what the linter refuses, is in [CONTRIBUTING.md](CONTRIBUTING.md).

## Deploy on Vercel

No environment variables and no database.

1. Import this repository. Framework preset: **Next.js**. Root directory: the repository root.
2. Install command: `npm ci` (the default).
3. Build command: `npm run build`. That runs `python3 tools/build_index.py` and then `next build`. Vercel's build image includes Python 3.
4. Optional: set `NEXT_PUBLIC_SITE_URL` to the production origin (`https://your-domain`) so canonical URLs and the sitemap use it.

The pages are statically generated from the catalog at build time. Blocked or warned skills fail the build, so a preview deploy cannot publish an entry the linter rejected.

## License

Apache-2.0. See [LICENSE](LICENSE).
