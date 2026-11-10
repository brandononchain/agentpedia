# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

People who write or run agent skills and need a reference they can trust: the skill’s job, the agent that bundles it, how to install it, and whether it passed the linter. They arrive with a name, a shelf, or a job to look up.

Inferred from the repository and Brandon’s redesign request. No separate interview tool was available in this session.

## Product Purpose

A reference encyclopedia of Agent Skills and the agents that bundle them. Every entry is linted before it ships, and the page shows the score. Success is finding the right entry, reading it, and copying an install snippet without guessing whether the file is safe to use.

## Positioning

The reference encyclopedia for agent skills and agents. Neighboring directories can list files. This one refuses to ship an entry that has a lint error or a warning, and it presents each entry as an article with its agent, shelf, score, and install path.

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

The display name is Agentpedia, set in `src/lib/site.ts`. The site is the reference encyclopedia of agent skills and agents. Brandon asked for structural cues from a general encyclopedia portal and a scholarly text library, and forbade copying their logos, wordmarks, exact layouts, or assets. Visual constraints he set: warm off-white paper, near-black ink, one restrained accent, a serif for reading, a sans for chrome, dark mode, and WCAG AA.

## Evidence on Hand

The catalog in `data/catalog.json` (39 skills, 8 agents, dated drops, lint scores, install snippets, the UC Irvine study URL, the Agent Skills spec URL, and the AAIF URL). No customer logos, testimonials, or version numbers exist. Do not invent them.

## Product Principles

- An entry is an article, not a product card.
- A missing fact is labeled missing.
- The lint result is part of the entry, not a marketing badge.
- Wayfinding is shelves, the alphabet, related entries, and the day something was added.
- The name is a label. The encyclopedia is the product.

## Accessibility & Inclusion

WCAG AA contrast, keyboard access, and a skip link. Brandon required these in the redesign request.
