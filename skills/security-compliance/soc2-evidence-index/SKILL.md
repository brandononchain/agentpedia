---
name: soc2-evidence-index
description: >-
  Indexes evidence the user already has against one trust-services category
  they name. Use when the user asks which document supports a SOC 2 control,
  including a dependency audit they paste.
license: Apache-2.0
metadata:
  category: security-compliance
  tags: compliance, evidence
  added: "2026-11-10"
  featured: false
---

# SOC 2 evidence index

Make a list of evidence the user already holds, and say which trust category it speaks to. Do not decide that a control is met.

## Steps

1. Ask which category the question is about if the user did not name one. The names are in [references/trust-categories.md](references/trust-categories.md).
2. List only documents, tickets, logs, or notes the user supplied. A dependency-audit note they paste is evidence of what that note says, not of a control passing.
3. For each item, write the date they gave, the category, and one sentence on what a reader can verify from it. If the date is missing, write "date not supplied".
4. Check the index by deleting any row whose document was not in the user's material.
5. End with the gaps: a category they asked about and did not support. Do not fill a gap with a document you invented.

## Example

User: For security, I have a March access review exported from the IdP and last week's dependency-audit notes for the API repo.

Agent: Two rows. The access review, date March, security: a reader can see who was reviewed. The dependency-audit notes, date last week, security: a reader can see the packages that note listed. Gap: nothing supplied speaks to how access is removed. The index does not say the control passed.

## Boundaries

An index is not a SOC 2 report and not a certification. Do not write an opinion a CPA would sign.
