---
name: workflow-permission-read
description: >-
  Reads permissions keys in a GitHub Actions workflow and checks each scope
  against the documented access levels. Use when the user asks what
  GITHUB_TOKEN access that file grants.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/read_permissions.py. Reads one local
  workflow file. No network and no extra packages.
metadata:
  category: devops-cloud
  subshelf: ci
  tags: actions, permissions
  added: "2026-11-20"
  featured: false
---

# Workflow permission read

Read the `permissions` keys in one workflow file and check each scope against the syntax example. Use [scripts/read_permissions.py](scripts/read_permissions.py). Which forms count, and which rules the script does not apply, is in [references/scope-rules.md](references/scope-rules.md).

## Steps

1. Take one workflow file. If the user has several, ask which file. Do not call the GitHub API, and do not assume the organization default.
2. Run `python3 scripts/read_permissions.py` on that file. The fixture is [assets/workflow.yml](assets/workflow.yml), and it is not the user's workflow.
3. Keep `ok`, `pull_request_target`, `skipped_permissions`, `duplicate_workflow`, and each printed scope. `workflow_form=absent` means the file has no top-level key. `job_form=absent` means that job has no key of its own.
4. For a map, keep `unspecified=none`. Do not copy the workflow scopes onto a job that has its own key, and do not invent a scope the script did not print.
5. Check each `scope` and `access` against that permissions block in the file. Drop a scope that is not on the printed line. `scope_ok=no` means the name is not in the syntax example, or the access token is not one that example allows for that name.
6. When `ok=no`, show the `reason`, `duplicate`, `duplicate_workflow`, or `duplicate_job` line and do not pick a winner. Do not change `write` to `read` because of a fork.

## Example

User: What token scopes does `assets/workflow.yml` set? Do not run it, and do not look up the repository default.

Agent: Runs `python3 scripts/read_permissions.py assets/workflow.yml`.

```
ok=yes
pull_request_target=no
skipped_permissions=0
duplicate_workflow=no
workflow_form=map
permissions_line=4
scope=contents
access=read
scope_ok=yes
unspecified=none
job=test
job_form=absent
job=release
job_form=map
permissions_line=13
scope=contents
access=write
scope_ok=yes
scope=id-token
access=write
scope_ok=yes
unspecified=none
jobs=2
```

The file sets `contents: read` for every job, and every other scope at that level is unspecified, so the script marks those `none`. `test` has no key of its own, so that workflow map is the one the file sets for it. `release` replaces that with `contents: write` and `id-token: write`, and its other scopes are unspecified. `pull_request_target` is not an event in this file. The repository default is not in the file, and nothing is changed on GitHub.

## Boundaries

Do not grant a permission, open a pull request, or claim the token in a live run matches this file. A fork pull request can still force `write` down to `read`, and `pull_request_target` has its own grant. Those rules are in the reference. This script does not apply them. Classifying action refs is action-uses-class. A failing log is ci-log-triage.
