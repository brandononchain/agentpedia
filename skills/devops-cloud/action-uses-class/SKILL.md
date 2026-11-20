---
name: action-uses-class
description: >-
  Classifies each GitHub Actions uses value as a full-length commit SHA, a
  movable ref, a same-repo path, or a Docker image. Use when the user asks
  whether a workflow pins an action before it runs.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/classify_uses.py. Reads one local workflow
  file. No network and no extra packages.
metadata:
  category: devops-cloud
  subshelf: ci
  tags: actions, pinning
  added: "2026-11-20"
  featured: false
---

# Action uses class

Classify every `uses` value in one workflow file. Use [scripts/classify_uses.py](scripts/classify_uses.py). Which strings count as a full-length SHA, and what the script does not check, is in [references/ref-forms.md](references/ref-forms.md).

## Steps

1. Take one workflow file. If the user has several, ask which file. Do not merge them, and do not fetch the actions.
2. Run `python3 scripts/classify_uses.py` on that file. The fixture is [assets/workflow.yml](assets/workflow.yml), and it is not the user's workflow.
3. For each value, keep `line`, `where`, `job`, `value`, `kind`, `ref`, `suffix`, and `prefix` as printed. Keep the counts at the end.
4. `kind=sha` is 40 hexadecimal characters after `@`. `kind=movable` is any other ref. `suffix=invalid` means a `$/` or `./` value also has `@`. `prefix=yes` means the ref starts with `refs/`.
5. Check a printed `value` against that line of the file. Drop a row whose value is not on that line. `ok=yes` means every `uses` value was classified. It does not mean the workflow is safe to run.
6. Do not edit the file, choose a SHA, or say a lockfile is present unless the user said so.

## Example

User: Classify the `uses` values in `assets/workflow.yml`. Do not run the workflow, and do not look up the commits.

Agent: Runs `python3 scripts/classify_uses.py assets/workflow.yml`.

```
ok=yes
line=7
where=step
job=test
value=actions/checkout@8f4b7f84864484a7bf31766abe9204da3cbe65b3
kind=sha
ref=8f4b7f84864484a7bf31766abe9204da3cbe65b3
suffix=no
prefix=no
line=9
where=step
job=test
value=actions/setup-node@v6
kind=movable
ref=v6
suffix=no
prefix=no
line=10
where=step
job=test
value=./.github/actions/hello-world-action
kind=relative
ref=absent
suffix=no
prefix=no
line=11
where=step
job=test
value=$/.github/actions/hello-world-action
kind=self-repo
ref=absent
suffix=no
prefix=no
line=12
where=step
job=test
value=docker://alpine:3.8
kind=docker
ref=absent
suffix=no
prefix=no
line=14
where=job
job=call
value=octo-org/this-repo/.github/workflows/workflow-1.yml@172239021f7ba04fe7327647b213799853a9eb89
kind=sha
ref=172239021f7ba04fe7327647b213799853a9eb89
suffix=no
prefix=no
uses=6
sha=2
movable=1
self_repo=1
relative=1
docker=1
missing_ref=0
expression=0
suffix_invalid=0
```

`actions/checkout` on line 7 is a 40-character SHA. `actions/setup-node@v6` is movable. The `./` and `$/` steps are paths in the same repository, and the Docker image is not a git ref. The job `call` is a reusable workflow pinned to a SHA. Nothing is edited, and no commit is fetched.

## Boundaries

Do not treat `kind=movable` as proof the action was compromised. A tag or a branch can move, and a full-length SHA can still point at a fork. This script does not resolve either one. If the user says the repository uses a workflow dependency lockfile, say this scan does not replace it. Do not rerun the workflow. A failing log is ci-log-triage.
