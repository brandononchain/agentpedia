# Agentpedia

[![skills](https://img.shields.io/badge/skills-105_linted-0e4f57?style=flat-square&labelColor=f4efe4)](https://github.com/brandononchain/agentpedia)
[![agents](https://img.shields.io/badge/agents-21-efe6d2?style=flat-square&labelColor=10110e)](https://github.com/brandononchain/agentpedia)
[![lint errors](https://img.shields.io/badge/lint_errors-0-ff5a36?style=flat-square&labelColor=10110e)](https://github.com/brandononchain/agentpedia/actions)
[![license](https://img.shields.io/badge/license-Apache--2.0-c9c0ae?style=flat-square&labelColor=10110e)](LICENSE)

Agentpedia is the open encyclopedia of agents and skills. The display name is `SITE_NAME` in `src/lib/site.ts`. Entries follow the [Agent Skills](https://agentskills.io/specification) format, now a project of the [Agentic AI Foundation](https://aaif.io/projects/agent-skills) at the Linux Foundation.

Most published skills do not meet their own authoring rules. In [From Anatomy to Smells](https://arxiv.org/abs/2607.01456), Hong, Imani, and Ahmed at UC Irvine studied 238 real `SKILL.md` files. 237 of them — over 99 percent — had at least one skill smell, and those smells rarely got fixed later.

The encyclopedia is the other way around. **Every entry is linted to 100 and given a static security audit before it is listed.** The site shows the lint score and the audit grade. The build fails if a skill has an error or a warning. An audit of on hold is not listed. The audit reads the files. It does not execute the entry.

Maintained by [Brandon](https://brandononchain.com) ([github.com/brandononchain](https://github.com/brandononchain)).

## Run it

Python 3.10+ and Node 22.

```bash
npm install
npm run dev
```

The dev server prints a local URL on port **43123**. `npm run dev` rebuilds `data/catalog.json` from `skills/` and `agents/` before Next.js starts.

```bash
npm run build         # lint the catalog, write certificates, sign if a key is set, build the Brain index, then next build
npm run test:lint     # skill-lint unit tests
npm run test:certs    # certificate and signing tests
npm run test:brain    # Brain search, trust, golden set, and the in-memory limiter
npm run lint:skills
```

## Layout

```
skills/<category>/<skill-name>/SKILL.md   # plus scripts/, references/, assets/
agents/<agent-name>/AGENT.md              # purpose, bundled skills, connectors, prompts
tools/skill-lint/                          # vendored dependency-free linter
tools/build_index.py                       # lints everything, audits it, and writes data/catalog.json
tools/audit/                               # static security audit, phase 1
tools/certlib.py                           # issues Listed records and publishes certificate JSON
tools/verify_checks.py                     # runs install probes and evals for Verified
tools/cert_sign.mjs                        # Ed25519-signs the canonical payload when a key is set
tools/build_brain_index.py                 # BM25 index for the Brain API and MCP server
tools/brain_key.py                         # create, revoke, and list Brain API keys in Upstash
certs/                                     # records, check manifests, and harness results
src/                                       # Next.js App Router site
```

The index carries the name, description, category, tags, lint score and findings, file tree, and install snippets for Claude Code, Codex, Cursor, and Grok Bot. The site is generated from that JSON.

## Add a daily entry

The daily shelf rotates through every directory under `skills/` that has a `category.json`, in alphabetical id order. One calendar day picks one shelf, and a run of days equal to the shelf count visits each shelf once. Empty shelves stay in that rotation so a new domain can receive an entry.

```bash
python3 tools/new_entry.py shelves
python3 tools/new_entry.py next-shelf
python3 tools/new_entry.py skill \
  --category "$(python3 tools/new_entry.py next-shelf)" \
  --subshelf notes \
  --name retry-notes \
  --description "Writes a retry policy from a handler. Use when the user asks how a call should retry." \
  --tags retries, http
```

```bash
python3 tools/new_entry.py agent \
  --name release-captain \
  --category docs-writing \
  --subshelf releases \
  --description "Prepares a changelog and release notes for a branch. Use when the user wants a release workflow." \
  --skills changelog-from-commits, release-notes-editor
```

`--subshelf` is required. On an existing shelf it must be a slug already listed in that shelf's `category.json`. A new shelf also needs `--label`, `--blurb`, `--subshelf-label`, and `--subshelf-description`. The shelf label and the sub-shelf label are title case (`Agent Ops & Evals`, `DevOps & Cloud`, `Sales & GTM`), with acronyms left in capitals. The folder slug stays lowercase. The shelf gets the next call number. Then edit the placeholder example, and run:

```bash
PYTHONPATH=tools/skill-lint python3 -m skill_lint skills/<category>/<name>
python3 tools/build_index.py
```

The quality bar, and what the linter refuses, is in [CONTRIBUTING.md](CONTRIBUTING.md).

## Certification

Every skill with a skill-lint score of 100 and a static audit that is not on hold, and every agent in the same position, gets a **Listed** certificate bound to the source commit and a sha256 digest of the entry directory. The digest covers the instructions and assets. It skips catalog placement: `category` and `subshelf` in the frontmatter, and the shelf number, sub-shelf order, and call number in `category.json`. **Verified** adds a real run of `tools/verify_checks.py` (an install probe and at least one eval). **Certified** adds a human review stored in `certs/records/<id>.json`. The reviewer cannot be the recorded author. The build refuses a Verified or Certified claim that does not have that evidence. Nothing in the current tree is Certified. Phase 1 of the audit is static. Sandbox, red-team, and manual review are recorded and are not gates yet.

| Route | What it is |
| --- | --- |
| `/certification` | What each tier checks, and what it does not guarantee |
| `/security` | Audit grades, and `/security/methodology` for the rules |
| `/submit` | How to add an entry, plus a prompt for a coding agent |
| `/submit.md` | The same steps as plain Markdown |
| `/certify` | The pull-request path for a Verified check run |
| `/cert/<id>` | One certificate, with embed snippets |
| `/cert/<id>.json` | The same record, plus an Ed25519 signature when a key is set |
| `/badge/<id>.svg` | The shields-style badge |
| `/.well-known/agentpedia-signing-key.json` | The public key |

A changed entry digest sets Verified and Certified to re-check pending. A Listed record is updated when lint is 100 and the audit is not on hold. Listed expires after 365 days, a verification run after 90 days, a review after 365 days, and a static audit after 90 days. Certified needs both the run and the review to be current. Details and the signing setup are in [certs/README.md](certs/README.md).

```bash
python3 tools/new_entry.py submit --kind skill --category <shelf> --subshelf <slug> --name <name> --description "<Third person. Use when the user asks for this job.>"
PYTHONPATH=tools python3 -m audit
```

```bash
python3 tools/signing_keygen.py
# commit certs/public-key.json only. The private file is base64 and is not printed.
# AGENTPEDIA_SIGNING_KEY accepts that base64 seed or a PKCS#8 PEM.
python3 tools/verify_certificate.py https://agentpedia.sh/cert/skill-csv-profile.json
```

Until that secret is set, records are unsigned on purpose (`signed: false`, `signature: null`).

## Brain

`/brain` documents the hosted search API and the MCP server at `/mcp`. `npm run build` writes `data/brain-index.json` and git ignores it. Do not hand-edit it.

Anonymous callers get 100 requests a day per IP. A key is `ap_live_` plus 32 letters or digits. `tools/brain_key.py` stores only `sha256(key)` in Upstash. Plans: free 1,000 calls a month, builder 25,000, team 150,000, enterprise custom (`monthlyLimit` on the key, otherwise 1,000,000). Paid plans are not billed yet.

## Deploy on Vercel

No database. Two optional secrets.

1. Import this repository. Framework preset: **Next.js**. Root directory: the repository root.
2. Install command: `npm ci` (the default).
3. Build command: `npm run build`. That runs `python3 tools/build_index.py`, `node tools/cert_sign.mjs`, `python3 tools/build_brain_index.py`, and then `next build`. Vercel's build image includes Python 3 and Node. No extra Python packages are required for signing.
4. The public origin is `https://agentpedia.sh`, read from `config/site.json`. Canonical URLs, Open Graph, the sitemap, badge embeds, and certificate records use that origin. Set `NEXT_PUBLIC_SITE_URL` only to override it.
5. Optional: set `AGENTPEDIA_SIGNING_KEY` to the base64 seed from `python3 tools/signing_keygen.py` (a PKCS#8 PEM still works), on Production and Preview, and as a GitHub Actions secret of the same name. The Catalog workflow passes it to the build and stays read-only. Commit `certs/public-key.json` and leave the private key out of the repo. Without the secret, the site still builds and the certificates say they are unsigned.
6. Optional: provision Upstash Redis from the Vercel Marketplace and set `UPSTASH_REDIS_REST_URL` and `UPSTASH_REDIS_REST_TOKEN` on Production and Preview. Without them the Brain runs keyless. Each server process keeps an in-memory limiter so previews and CI still answer.

| Variable | Required | What it does |
| --- | --- | --- |
| `NEXT_PUBLIC_SITE_URL` | No | Overrides the public origin in `config/site.json`. |
| `AGENTPEDIA_SIGNING_KEY` | No | Base64 Ed25519 seed, or PKCS#8 PEM. Signs certificates at build time. |
| `UPSTASH_REDIS_REST_URL` | No | Upstash REST endpoint for Brain keys, rate limits, and monthly usage. |
| `UPSTASH_REDIS_REST_TOKEN` | No | Token for that Redis database. |

The pages are statically generated from the catalog at build time. Blocked or warned skills fail the build, so a preview deploy cannot publish an entry the linter rejected.

## License

Apache-2.0. See [LICENSE](LICENSE).
