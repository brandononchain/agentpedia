---
name: security-and-hardening
description: >-
  Reviews code the user pasted for missing checks on untrusted input, secrets
  in logs, and auth gaps, and names a control for each gap. Use when the user
  asks for a hardening pass on a handler, a login flow, or a storage path.
license: MIT
metadata:
  category: security-compliance
  subshelf: secrets
  tags: security, hardening, review
  added: "2026-11-25"
  featured: false
  source: import
  author: Addy Osmani
  authorUrl: "https://github.com/addyosmani"
  authorKind: person
  curator: Brandon
  upstream: addyosmani/agent-skills
  upstreamCommit: e997ac5b9a74eab332d5e9793bb38a38c8cfdd74
  upstreamPath: skills/security-and-hardening/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2025 Addy Osmani
---

# Security and hardening

Do this one job: a hardening note for code the user pasted. Adapted from `addyosmani/agent-skills` at commit `e997ac5b9a74` (MIT). Copyright (c) 2025 Addy Osmani

## Steps

1. Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.
2. List the trust boundaries in the paste: request fields, file uploads, webhooks, and third-party responses. Do not invent an endpoint that is not in the paste.
3. For each boundary, note a missing check: untrusted input used raw, a secret written to a log, or an action with no auth check. Quote the line. If a secret is visible, name the kind and the line, and do not copy the secret into the note.
4. Name one control for each gap: validate, encode, authorize, or stop writing the secret. Pair it with a test that would fail if the control were absent.
5. State the misuse in one plain sentence. Do not include a payload, a request, a bypass, or exploit steps.
6. If the paste is too small to judge a boundary, say so and ask for the handler. Do not fill the gap with a generic checklist.
7. Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.

## Example

User: Review this handler. It logs `req.body.token` and then runs `db.query("select * from t where id=" + req.query.id)` with no session check.

Agent: Two gaps, each with the line: the token is written to the log, and the id is concatenated into a query with no auth check. Controls: stop logging the token, and bind the id as a parameter after an auth check. No payload included.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide. It does not produce an exploit.
