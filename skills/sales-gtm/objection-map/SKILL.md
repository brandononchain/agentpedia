---
name: objection-map
description: >-
  Lists real objections and a response grounded in the product, including when
  the objection should end the deal. Use when the user asks how to handle sales
  objections or to prep a call.
license: Apache-2.0
metadata:
  category: sales-gtm
  tags: objections, sales
  added: "2026-11-05"
  featured: false
---

# Objection map

Build an objection map from the product the user described and the objections they have actually heard. A response that the product cannot support is not a response. Some objections should end the conversation.

## Steps

1. List the objections the user supplied. If they supplied none, draft likely objections and label them "unheard — confirm before using."
2. For each objection, write a reply that uses only product facts the user provided, plus one question that checks whether the objection is the real one.
3. Mark objections that should disqualify the deal when the product truly does not fit.
4. Add the proof that would make the reply believable (a doc, a sample, a lint report). If the proof does not exist, say "proof missing."
5. Validate the map: no reply promises a feature that was not in the brief, and every disqualification is tied to a real limit.

## Example

User: Product lints skills in a public repo. It does not host private skills yet. Heard objection: "We cannot put our skills in a public catalog."

Agent: Reply — Skilldex reviews public entries; private hosting is not available, so this catalog is the wrong place for unreleased skills. Question — do you need a private checker, or a place to publish the skills you already open-source? This objection disqualifies a buyer who needs privacy. Proof missing for a private tier, because it does not exist.

## Boundaries

Do not tell the user to pressure past a disqualifying objection. Do not invent a customer logo.
