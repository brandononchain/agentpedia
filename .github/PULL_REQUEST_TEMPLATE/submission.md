## Entry

- Kind: skill or agent
- Name:
- Shelf:

## What it does

## What it refuses

## Checks

- [ ] `PYTHONPATH=tools/skill-lint python3 -m skill_lint` scores 100 for a skill (zero errors, warnings, and info findings)
- [ ] `PYTHONPATH=tools python3 -m audit --path <entry>` is passed, or warning with days of grace left
- [ ] The entry is not on hold
- [ ] This pull request does not force-push

Lint score:

Audit grade and status:
