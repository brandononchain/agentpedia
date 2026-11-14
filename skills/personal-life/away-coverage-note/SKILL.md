---
name: away-coverage-note
description: >-
  Checks a house-coverage list against the dates the user will be away. Use
  when the user asks for a note for the person watching the home. It does not
  book the trip and it does not store a code or a password.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/coverage_check.py. No network and no extra
  packages.
metadata:
  category: personal-life
  tags: home, travel
  added: "2026-11-13"
  featured: false
---

# Away coverage note

Turn a list the user already wrote into a note for the person watching the home. The limits are in [references/coverage-note.md](references/coverage-note.md). Do not book the trip, and do not add a task they did not type.

## Steps

1. Record the away start and away end as dates they stated. The CSV needs `item`, `owner`, `window_start`, `window_end`, and `instruction`. The fixture is [assets/sample.csv](assets/sample.csv).
2. Run `python3 scripts/coverage_check.py` on that file with `--away-start` and `--away-end`.
3. Read `items`, `incomplete`, `outside`, `duplicate`, `secretish`, and `ready`. A row flag names which of those failed.
4. If `ready=no`, name the flags and stop. Do not rewrite an instruction so the row looks finished, and do not copy a code into the reply.
5. If `ready=yes`, show the rows. Check that every item, owner, window, and instruction matches the file, and that no row was added. Do not contact the owner.

## Example

User: Check `assets/sample.csv` for 2026-12-01 through 2026-12-08. Do not email Sam.

Agent: The script prints `away=2026-12-01..2026-12-08`, `items=2`, `incomplete=0`, `outside=0`, `duplicate=0`, `secretish=0`, `ready=yes`. Fern is Sam, Water on Tuesday and Friday. Mail is Sam, Leave packages inside the door. Both windows match the file. Nothing is added, and Sam is not contacted.

## Boundaries

Do not book travel. Do not invent a plant, a pet, a bill, or a spare key. If an instruction mentions medicine, copy the words they wrote and do not add a dose. That line is informational only and is not medical advice. A door code, alarm code, or password stays out of the note. The user shares that in person.
