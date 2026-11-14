---
name: secret-scan-report
description: >-
  Reports line numbers where pasted text looks like a token, a cloud key, or a
  private-key header. Use when the user asks whether a diff, a log, or a note
  contains a secret.
license: Apache-2.0
metadata:
  category: security-compliance
  subshelf: secrets
  tags: secrets, scanning
  added: "2026-11-10"
  featured: false
---

# Secret scan report

Look for token-shaped strings in text the user already has. Report the line and the kind. Do not repeat the secret, and do not send the file anywhere.

## Steps

1. Confirm the file or the paste. Refuse a request to scan a machine, a network, or a repository the user did not put in front of you.
2. Run `python3 scripts/scan_text.py` on that file. The sample is [assets/sample.txt](assets/sample.txt).
3. For each printed line, record the line number and the kind (`aws-access-key`, `github-token`, `openai-key`, `slack-token`, `private-key`, or `high-entropy`).
4. Check the count against the `findings=` line. If the user asks what to do next, say to revoke the credential and to remove it from the file. Do not invent a rotation procedure for a vendor you were not given.

## Example

User: Scan `assets/sample.txt`.

Agent: Line 2 is a `github-token`. Line 3 is an `aws-access-key`. The script prints `findings=2`. The values are not copied into the report. The last line has no finding.

## Boundaries

A clean scan is not proof that a secret is absent. The script only matches shapes it knows. Do not claim the file is safe to commit.

## References

The shape list follows the detector classes used by [gitleaks](https://github.com/gitleaks/gitleaks): known prefixes, private-key headers, and high-entropy tokens. The patterns in `scripts/scan_text.py` are original and shorter than that project's ruleset.
