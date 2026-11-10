# skill-lint

A small, dependency-light Python CLI that lints [Agent Skills](https://agentskills.io/specification) (`SKILL.md`). It checks the open spec (required frontmatter, naming, length limits), progressive-disclosure hygiene, common [skill-smell](https://arxiv.org/abs/2607.01456) categories, and a few high-signal safety patterns.

No third-party runtime dependencies. Python 3.10+.

## Install

From this directory:

```bash
python3 -m pip install -e .
skill-lint path/to/skills
```

Or run without installing:

```bash
./skill-lint path/to/skills
python3 -m skill_lint path/to/skills
```

## Usage

```bash
skill-lint <path>
skill-lint --json <path>
```

`path` may be:

- a `SKILL.md` file
- a skill folder that contains `SKILL.md`
- a parent folder of skill folders (discovered recursively)

Human-readable text is the default. `--json` prints a machine-readable report. The process exits `1` if any **error** was found, and `0` otherwise (warnings and info do not fail the run).

## Rules

Each finding has an id, a severity (`error` / `warn` / `info`), a one-line message, and a fix hint.

### Spec

| Id | Severity | What it checks |
| --- | --- | --- |
| `spec.frontmatter.missing` | error | File must start with YAML frontmatter between `---` lines |
| `spec.frontmatter.invalid` | error | Frontmatter must parse as simple YAML keys |
| `spec.filename.case` | error | File must be named `SKILL.md` (Linux is case-sensitive) |
| `spec.name.missing` | error | `name` is required and non-empty |
| `spec.name.invalid` | error | Lowercase letters, numbers, single hyphens; no leading/trailing/`--` hyphens |
| `spec.name.too-long` | error | `name` max 64 characters |
| `spec.name.directory-mismatch` | error | `name` must match the parent folder |
| `spec.description.missing` | error | `description` is required and non-empty |
| `spec.description.too-long` | error | `description` max 1024 characters |
| `spec.compatibility.too-long` | error | `compatibility` max 500 characters |

### Skill smells and progressive disclosure

| Id | Severity | What it checks |
| --- | --- | --- |
| `smell.name.unclear` | warn | Name is too generic (`misc`, `helper`, `dig`, …) or shorter than 3 characters |
| `smell.description.no-when` | warn | Description does not say when to use the skill |
| `smell.description.vague` | warn | Description shorter than 40 characters |
| `smell.description.not-third-person` | info | Description uses I/you phrasing |
| `smell.description.xml` | error | XML/HTML tags in the description (prompt-injection smell) |
| `smell.body.too-long-lines` | warn | Body longer than 500 lines |
| `smell.body.too-long-words` | warn | Body longer than 5000 words |
| `smell.body.huge-inline-blob` | warn | A fenced block of 80+ lines that should live in `references/` or `scripts/` |
| `smell.example.missing` | warn | No example of inputs, outputs, or usage |
| `smell.workflow.stepless` | warn | Longer bodies with no numbered steps |
| `smell.validation.missing` | info | No mention of validate/verify/check/test |
| `smell.scripts.missing` | info | Many shell commands but no `scripts/` helpers |
| `smell.detail.undelegated` | warn | Very long body with nothing moved into `references/` |

### Links

| Id | Severity | What it checks |
| --- | --- | --- |
| `link.relative.missing` | error | Relative Markdown links or `scripts/` / `references/` / `assets/` paths that do not exist |
| `link.path.backslash` | warn | Windows-style backslash paths |

### Safety

| Id | Severity | What it checks |
| --- | --- | --- |
| `security.secret` | error | Hardcoded keys, tokens, passwords, or private key blocks |
| `security.absolute-path` | warn | Machine-specific absolute paths (`/Users/`, `/home/`, `C:\`, …) |
| `security.curl-pipe-sh` | error | `curl … \| sh` / `wget … \| bash` |
| `security.rm-rf` | warn/error | `rm -rf` (error if aimed at `/`, `/*`, or `$HOME`) |
| `security.exfil-url` | warn | webhook.site, ngrok, Discord webhooks, pastebin, and similar sinks |

Scan-level ids: `scan.path.missing`, `scan.skill.not-found`, `scan.file.unreadable`.

## Tests

```bash
python3 -m pip install pytest
python3 -m pytest -q
```

Fixtures under `tests/fixtures/` cover a clean skill, missing/invalid frontmatter, unsafe shell, broken links, a huge inline blob, and a lowercase `skill.md` filename.

## Example

```bash
skill-lint tests/fixtures/good-pdf
skill-lint tests/fixtures
skill-lint --json /home/box/agent-data/workflows
```
