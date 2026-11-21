# Sourcing queue

`source_candidates.py` searches public Agent Skills and writes `data/candidates.json`. That file is generated. Rebuild it with the script. Do not hand-merge it.

The committed queue keeps compatible and readme-only rows (MIT, Apache-2.0, BSD, ISC, CC-BY, CC0, Unlicense, or a README claim that still needs a LICENSE file). Unknown and copyleft rows are left out. If the file would pass about 2 MB, the script keeps the top 1,500 compatible rows by score and says so in `note`.

Each row has `name`, `sourceUrl`, `repo`, `path`, `license`, `licenseState` (`compatible`, `readme-only`, and, while the script is still deciding, `unknown` or `copyleft`), `shelf`, `score`, `status` (`queued`, `imported`, `rejected`), and `reason`. A later run keeps imported and rejected rows so it does not retry them.

```bash
python3 tools/sourcing/source_candidates.py
python3 tools/sourcing/source_candidates.py --from-snapshot path/to/candidates.json
```

The script reads `data/catalog.json` and drops names already in the catalog. It uses the `gh` CLI when that is logged in, otherwise the public GitHub API (`GH_TOKEN` or `GITHUB_TOKEN`). Responses cache under `tools/sourcing/cache/`, which is gitignored.

GitHub Actions runs this nightly (and on `workflow_dispatch`) from `main` only. The job pushes `data/candidates.json` to the `candidates` branch and opens or updates a pull request titled "Refresh candidate queue". It does not push to `main` and it does not run on pull requests.

## Import

```bash
python3 tools/new_entry.py import --from https://github.com/owner/repo/blob/main/skills/name/SKILL.md
python3 tools/new_entry.py import --from https://github.com/owner/repo --shelf product
python3 tools/new_entry.py import --next 8 --prefer-empty-shelves
```

`--next` walks queued compatible rows that have a `SKILL.md` path. `--prefer-empty-shelves` takes Education, Product, and People before other shelves, then shelves with fewer skills, and prefers official orgs (Anthropic, GitHub, Google, Addy Osmani, and the other orgs listed in the script). It keeps going until that many imports succeed or the queue runs out. A name already in the catalog is skipped when the text matches, and imported under a disambiguated name when the text differs.

Import pins the commit SHA, fetches `SKILL.md`, and fetches a small bundled file only when the adapted entry still links to it. The entry records the upstream repo, commit, path, license, and copyright, and names the author:

- `author` is a stated name from the skill frontmatter, the LICENSE copyright line, or the GitHub profile `name`. If none of those exist, it is the GitHub login. The importer does not invent a person's name.
- `authorUrl` is the GitHub profile or organization URL.
- `curator` is Brandon (`https://github.com/brandononchain`).

The book page links the author, shows "Curated by Brandon", and links "Adapted from `<repo>` @ `<short sha>` (`<license>`)" at the pinned file. Popularity of the upstream repo does not set Verified. The catalog build issues Listed when lint is 100 and the audit is not on hold.

## License rules

Import only when the license is MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, CC-BY-4.0, CC0-1.0, or Unlicense.

Do not import GPL, AGPL, LGPL, or CC-BY-SA. A readme-only license is rejected until a LICENSE file is fetched and matches the allow list. A failed lint score (anything under 100) or an audit that is on hold or grade F deletes the folder and marks the row rejected with the reason.

The adaptation is one job in Agentpedia's voice. Vendor telemetry and install pings are removed. `NOTICE` gains a copyright line and the pinned source URL.
