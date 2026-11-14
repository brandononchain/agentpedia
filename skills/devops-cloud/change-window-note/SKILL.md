---
name: change-window-note
description: >-
  Writes who changes production, when the window opens and closes, and how to
  stop. Use when the user asks for a change window before a deploy or a config
  edit on Vercel, AWS, or Docker.
license: Apache-2.0
metadata:
  category: devops-cloud
  subshelf: deploys
  tags: incidents, deploys
  added: "2026-11-10"
  featured: false
---

# Change window note

Write the window from facts the user supplies. An incident timeline is a different skill: that one is written after something broke. This one is written before the change.

## Steps

1. Record the change in one sentence, the environment, and the start and end the user gave. If an end is missing, the window is not ready.
2. Name the person who will make the change and the person who can stop it. If those are the same person, say so.
3. Copy the rollback they stated. If they have no rollback, write "stop: not stated" and do not invent one.
4. Note anything they said must not run during the window (a migration, a broadcast, a customer demo).
5. Check every name and time against the user's text. End with ready or not ready. Not ready if the end, the owner, or the stop is missing.

## Example

User: Tomorrow 15:00 to 15:30 UTC I will raise the API container count on ECS. Sam can tell me to stop. Rollback is the previous desired count, which is 3.

Agent: Change: raise the API container count on ECS. Window: tomorrow 15:00–15:30 UTC. Owner: the user. Stop: Sam, by restoring desired count 3. Ready. The note does not apply the change.

## Boundaries

Do not open the window, page anyone, or widen the time. Do not describe this as an incident writeup.
