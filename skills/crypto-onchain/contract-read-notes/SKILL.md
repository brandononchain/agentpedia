---
name: contract-read-notes
description: >-
  Reads a contract or ABI the user pasted and notes who can move assets or
  change the code, in their own words. Use when the user asks for a
  smart-contract reading. The skill does not move funds or sign a transaction.
license: Apache-2.0
metadata:
  category: crypto-onchain
  subshelf: contracts
  tags: contracts, review
  added: "2026-11-10"
  featured: false
---

# Contract read notes

Answer reading questions from code or an ABI the user pasted. This skill is read-only. It does not move funds or sign a transaction. A reading is not an audit.

## Steps

1. Say whether the paste is source, an ABI, or both. If a function is not in the paste, do not assume it exists.
2. Answer only these questions, and only when the paste shows the answer: who can call a function that transfers tokens, who can upgrade or replace the code, and whether the paste shows a pause. If the paste does not show it, write "not shown".
3. Quote the function name for each answer. Do not describe how to abuse a function, and do not write a call that would move assets.
4. Check that every function name you cited is in the paste.
5. Close with: this is not an audit, and no transaction was signed.

## Example

User: The ABI includes `transfer(address,uint256)` and `setPaused(bool)`. The source comment says `setPaused` is `onlyOwner`. There is no upgrade function in the paste.

Agent: `transfer` is in the ABI. The paste does not say who may call it, so that is not shown. `setPaused` is in the ABI and the source comment says `onlyOwner`. Upgrade is not shown. This is not an audit. Nothing is signed, and no call is drafted.

## Boundaries

Do not write an exploit, a calldata payload, or a transaction. Do not claim the contract is safe.
