---
name: citation-checker
description: >-
  Checks a draft against the sources provided and marks claims the sources do
  not support. Use when the user asks to verify citations, fact-check a writeup,
  or see which sentences need a source.
license: Apache-2.0
metadata:
  category: web-research
  tags: research, citations
  added: "2026-11-06"
  featured: false
---

# Citation checker

Check a draft against the sources the user provides. Mark support, not support, or unclear. Do not "fix" a claim by quietly changing it.

## Steps

1. Split the draft into checkable claims. Skip pure opinion that the draft labels as opinion.
2. For each claim, find the passage in the supplied sources that supports it, or record that no passage does.
3. Label each claim supported, unsupported, or unclear. Unclear means the source is about the topic but does not state the claim.
4. Quote or closely paraphrase the supporting passage and name the source. Keep quotes short.
5. Validate the report by confirming you did not mark a claim supported without a passage. Offer a revised sentence only for unsupported claims, and only as a suggestion beside the original.

## Example

User: Draft says "Over 99% of 238 SKILL.md files had at least one skill smell." Source is the UC Irvine paper abstract stating that finding.

Agent: Supported. The abstract states that over 99% of the 238 files contain at least one skill smell. No wording change.

## Boundaries

Do not use a source that was not provided. Do not treat a title as support for a statistic in the body.
