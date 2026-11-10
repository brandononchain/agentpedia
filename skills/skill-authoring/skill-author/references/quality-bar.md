# Agentpedia quality bar

A skill ships when skill-lint reports zero errors and zero warnings.

## Shape

- The folder name matches `name`.
- `description` is third person, says what the skill does, and says when to use it.
- The body has numbered steps, one realistic example, and a validation check.
- Relative links and `scripts/`, `references/`, and `assets/` paths point at real files.
- Detail that is not needed on every run lives in `references/`.

## Safety

- No hardcoded credentials or private keys.
- No download piped into a shell.
- No recursive force-delete.
- No machine-specific absolute paths.
- No unexpected webhook, tunnel, or paste-site endpoints.

## Check

From a Agentpedia checkout:

```
PYTHONPATH=tools/skill-lint python3 -m skill_lint skills/<category>/<name>
```

Read the hints. An error fails the entry. A warning means the skill is not ready for this catalog.
