# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

People who write or run agent skills and need a reference they can trust: the skill’s job, the agent that bundles it, how to install it, whether it passed the linter, and the static audit grade. They arrive with a name, a shelf, or a job to look up.

Inferred from the repository and Brandon’s redesign request. No separate interview tool was available in this session.

## Product Purpose

The open encyclopedia of agents and skills. Every entry is linted to 100 and given a static security audit before it is listed, and the page shows both results. Success is finding the right entry, reading it, and copying an install snippet with the audit grade in view. The audit reads files. It does not execute the entry, and it does not claim the entry is safe against a hostile user.

## Positioning

The open encyclopedia of agents and skills. Neighboring directories can list files. This one refuses to ship an entry that has a lint error or a warning, holds back an entry the static audit puts on hold, and presents each entry as an article with its agent, shelf, lint score, audit grade, and install path.

## Operating Context

The catalog is generated from `skills/` and `agents/` by `tools/build_index.py`. The site is a static Next.js app. Daily drops are dated in each entry. Install snippets target Claude Code, Codex, Cursor, and Grok Bot. Brandon maintains the project (github.com/brandononchain, brandononchain.com).

## Capabilities and Constraints

- Keep every existing route. New routes may be added. If a path changes, leave a redirect.
- Keep the lint gate, `tools/build_index.py`, CI, and install snippets working. Every entry still scores 100.
- Search may run in the browser over `catalog.json`.
- Do not invent prices, versions, rules, or social proof. Skills do not record a version; the infobox says so.
- The display name is Agentpedia, stored in `src/lib/site.ts` as `SITE_NAME`.
- Trading and marketing skills still only record and draft. The site does not place orders or post.

## Brand Commitments

The display name is Agentpedia, set in `src/lib/site.ts`. The site is the open encyclopedia of agents and skills. Brandon asked for structural cues from a general encyclopedia portal and a scholarly text library, and forbade copying their logos, wordmarks, exact layouts, or assets. Visual constraints he set: warm off-white paper, near-black ink, one restrained accent, a serif for reading, a sans for chrome, dark mode, and WCAG AA.

## Evidence on Hand

The catalog in `data/catalog.json` (skills, agents, shelves, dated drops, lint scores, static audit grades, install snippets, the UC Irvine study URL, the Agent Skills spec URL, and the AAIF URL). Counts come from that file. No customer logos, testimonials, or version numbers exist. Do not invent them.

## Product Principles

- An entry is an article, not a product card.
- A missing fact is labeled missing.
- The lint result and the static audit are part of the entry, not a marketing badge.
- Wayfinding is shelves, the alphabet, related entries, and the day something was added.
- The name is a label. The encyclopedia is the product.

## Accessibility & Inclusion

WCAG AA contrast, keyboard access, and a skip link. Brandon required these in the redesign request.
