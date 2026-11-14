---
name: device-switch-list
description: >-
  Lists accounts and files the user says must move to a new device, and where
  they said each one lives. Use when the user is replacing a phone or a
  computer. It does not sign in and it does not print a one-time code.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/switch_check.py. No network and no extra
  packages.
metadata:
  category: personal-life
  subshelf: devices
  tags: devices, accounts
  added: "2026-11-13"
  featured: false
---

# Device switch list

Check a move list the user already wrote before they replace a phone or a computer. Why an authenticator does not come along with photos is in [references/what-moves.md](references/what-moves.md). Do not sign in, and do not print a code.

## Steps

1. Confirm the CSV has `account`, `kind`, `must_move`, and `where`. `kind` is `login`, `authenticator`, `files`, `subscription`, or `other`. The fixture is [assets/sample.csv](assets/sample.csv).
2. Run `python3 scripts/switch_check.py` on that file.
3. Read `rows`, `must_move`, `missing_where`, `secretish`, `bad_kind`, and `ready`.
4. If `ready=no`, name the flags and stop. Do not fill in a place the user did not write, and do not type a code or a password to make `secretish` go away.
5. If `ready=yes`, show the rows. Check that every account, kind, and place matches the file. An empty place is allowed only when `must_move` is `no`. Do not sign in.

## Example

User: Check `assets/sample.csv` before replacing a phone. Do not sign in.

Agent: The script prints `rows=4`, `must_move=3`, `missing_where=0`, `secretish=0`, `bad_kind=0`, `ready=yes`. Email is an authenticator in the password manager. Photo library is files on an external drive. Editor license is a subscription in an email receipt. News app is a login with `must_move=no`, so the empty place is left empty. No account is added, and nothing is signed in.

## Boundaries

Do not claim a sign-in method will transfer because a contact list will. Do not invent a backup the user did not name. `ready=yes` means the list is complete on the page. It does not mean the new device already has the accounts.
