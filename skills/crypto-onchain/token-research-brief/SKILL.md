---
name: token-research-brief
description: >-
  Briefs a token from sources the user supplies, and keeps claims tied to those
  sources. Use when the user asks for token research. The skill does not move
  funds or sign a transaction, and it does not say to buy or sell.
license: Apache-2.0
metadata:
  category: crypto-onchain
  tags: tokens, research
  added: "2026-11-10"
  featured: false
---

# Token research brief

Write what the sources say. This skill is read-only. It does not move funds or sign a transaction, and it does not recommend a trade.

## Steps

1. Name the token exactly as the user did, including the chain if they named one. Do not guess a contract address.
2. For each claim (what it is, who operates it, supply, a recent event), cite the source they pasted. A claim with no source is left out.
3. Separate description from numbers. A supply figure is included only when a source states it.
4. Check the brief by listing the sources at the bottom and confirming each claim points at one of them.
5. End with: this is not a recommendation to buy, sell, or hold, and no transaction was signed.

## Example

User: Sources: the project page says ExampleToken is a governance token on Base. The explorer paste says total supply 1,000,000. Nothing about who holds it.

Agent: The brief says it is a governance token on Base, sourced to the project page, and that the explorer paste states a total supply of 1,000,000. Holders are not in the sources, so they are omitted. The brief says this is not a recommendation, and it does not sign or send anything.

## Boundaries

Do not tell the user to buy or sell. Do not invent a contract address, a holder list, or a price.
