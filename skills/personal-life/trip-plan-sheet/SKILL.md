---
name: trip-plan-sheet
description: >-
  Builds a trip sheet from dates, a city, and constraints the user states.
  Use when the user asks to plan travel and has the dates or the limit in the
  message.
license: Apache-2.0
metadata:
  category: personal-life
  subshelf: travel
  tags: travel, planning
  added: "2026-11-10"
  featured: false
---

# Trip plan sheet

Lay out a trip from constraints. Do not book anything, and do not invent a price or an opening hour.

## Steps

1. Record the dates, the city or cities, and who is going, as they stated. A missing date stays "date not set" and the sheet does not pretend the trip is booked.
2. List constraints they named: budget, mobility, a must-see, a no-go. A constraint they did not name is not added.
3. Propose a day-by-day order using only places they named. If they named none, the sheet is a list of open questions, not a sightseeing list from memory.
4. Check the sheet so no price, address, or hour appears unless they typed it. Mark anything that still needs a booking as not booked.
5. Hand it back. Do not reserve a seat or a room.

## Example

User: Two days in Lisbon in March, dates not set. Must see the tile museum. No budget typed. Do not book.

Agent: Dates are not set. The only place on the sheet is the tile museum they named. Nothing is booked, and no price or hour is added.

## Boundaries

Do not book travel. Do not invent a fare, a visa rule, or a closed day.
