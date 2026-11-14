---
name: wallet-watch-note
description: >-
  Writes a read-only note of balances and transfers the user pasted for one
  address. Use when the user asks to watch a wallet. The skill does not move
  funds or sign a transaction.
license: Apache-2.0
metadata:
  category: crypto-onchain
  subshelf: wallets
  tags: wallets, onchain
  added: "2026-11-10"
  featured: false
---

# Wallet watch note

Record what the user pasted. This skill is read-only. It does not move funds or sign a transaction.

## Steps

1. Copy the address exactly. If they pasted a name instead of an address, say the address was not supplied and do not look one up.
2. List each balance they supplied: asset, amount, and the time they said it was observed. A balance they did not paste is omitted.
3. List transfers they pasted, with direction (in or out), asset, amount, and counterparty if they included one. Do not infer a missing counterparty.
4. Check the note so every amount appears in their paste. Do not convert to a dollar value unless they also pasted a price, and then show that price beside the conversion.
5. State again that nothing was signed and no transaction was sent.

## Example

User: Address 0xabc…123 held 2 ETH at 2026-11-10 09:00 UTC according to the explorer paste. One outbound of 0.1 ETH to 0xdef…456 is in the same paste. No price.

Agent: The note lists 2 ETH at that time and one outbound of 0.1 ETH to the counterparty they pasted. No fiat value is added. No transaction is signed or sent.

## Boundaries

Do not connect to a wallet, request a signature, or suggest a transfer. Do not claim the balance is current after the timestamp they gave.
