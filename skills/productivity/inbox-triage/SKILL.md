---
name: inbox-triage
description: >-
  Sorts a pasted inbox into reply, delegate, read later, and drop, with a one-
  line reason for each message. Use when the user asks to triage email or a pile
  of messages.
license: Apache-2.0
metadata:
  category: productivity
  tags: inbox
  added: "2026-11-05"
  featured: false
---

# Inbox triage

Sort messages the user pastes. Do not reply to anyone. The output is a sorted list they can act on.

## Steps

1. Read each message subject and sender. If the body is missing and the subject is ambiguous, park it in read later with the reason "body not pasted."
2. Assign one bucket: reply (needs this user), delegate (a named other person should handle it), read later (useful, not time-sensitive), or drop (no action, or noise).
3. Add one short reason. For reply, name the question to answer, not a full draft, unless the user asked for drafts.
4. Order the reply bucket by any deadline stated in the message. Do not invent urgency.
5. Validate that every pasted message appears in exactly one bucket. Do not send, forward, or delete anything.

## Example

User pastes three subjects: "Please review the skill today" from Sam, "Your receipt" from a vendor, and "Can Alex own the launch post?" from Sam.

Agent: Reply — Sam, review the skill, deadline today. Delegate — Sam's question, Alex named as the owner, so confirm with Alex rather than writing the post. Drop — the receipt, unless the user said they reconcile receipts. Nothing is sent.

## Boundaries

Do not open links in the messages. Do not draft a reply that agrees to a contract, a payment, or a meeting time the user has not chosen.
