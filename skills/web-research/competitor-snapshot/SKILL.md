---
name: competitor-snapshot
description: >-
  Compares products on a fixed rubric: who it is for, the job it does, pricing
  if public, and what is not known. Use when the user asks for a competitor
  snapshot or a market comparison.
license: Apache-2.0
metadata:
  category: web-research
  tags: research, competitors
  added: "2026-11-06"
  featured: false
---

# Competitor snapshot

Compare a small set of products on the same rubric. Use public information the user supplied or that a search just returned. Missing cells stay missing.

## Steps

1. List the products and the date of the snapshot. Keep the set to the products the user named, up to five.
2. For each product, fill the same fields: who it is for, the job it claims to do, pricing if a public price was found, and the source for each field.
3. Add one row for "not shown" so gaps are visible.
4. Write three sentences on real differences. Do not rank a "winner" unless the user asked for a recommendation and gave the criteria.
5. Validate that every filled cell has a source from this session. Clear any cell you cannot source.

## Example

User: Snapshot Skilldex against a generic unreviewed skill marketplace, using only this brief: Skilldex lints every entry before it ships; the other listing does not claim a review.

Agent: Skilldex is for people who want a skill that has passed a published linter. The other listing is for browsing a large unreviewed catalog. Pricing is not shown for either. Difference — one refuses an entry with lint errors, and the other does not say it checks. No winner is declared.

## Boundaries

Do not invent prices, traffic, or customer quotes. Do not disparage a product beyond the sourced difference.
