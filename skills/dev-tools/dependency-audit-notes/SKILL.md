---
name: dependency-audit-notes
description: >-
  Reads a dependency diff and notes major bumps, new install scripts,
  unmaintained packages, and license changes. Use when the user asks to review a
  lockfile update or a dependency bump.
license: Apache-2.0
metadata:
  category: dev-tools
  subshelf: dependencies
  tags: dependencies, review
  added: "2026-11-08"
  featured: false
---

# Dependency audit notes

Review a dependency change from the manifest and lockfile diff the user provides. Explain what a human should look at before merging. Do not run install scripts.

## Steps

1. List packages whose version changed, plus packages added or removed. Ignore hash-only lockfile noise when the resolved version did not change.
2. Mark major bumps and any package that is new to the repo.
3. Call out install scripts, native builds, postinstall hooks, and license changes when the diff or the package metadata shows them. If metadata was not provided, say it was not checked.
4. Note packages the user flagged as abandoned, or that the diff shows moving to a deprecated name.
5. Validate the notes against the diff: every package you mention must appear in it. End with merge as-is, read the changelog first, or hold.

## Example

User: Review a diff that bumps `image-lib` from 2.4.1 to 3.0.0 and adds `preview-worker`.

Agent: `image-lib` is a major bump; read its changelog for removed exports before merging. `preview-worker` is new and was not in the previous lockfile; its license and install scripts were not in the diff, so those are unchecked. Recommendation: read the changelog first.

## Boundaries

Do not claim a package is free of vulnerabilities without an advisory the user supplied. Do not execute the package.
