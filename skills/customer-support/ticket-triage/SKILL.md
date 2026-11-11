---
name: ticket-triage
description: >-
  Sorts pasted support tickets into reply, wait, bug, or billing, with the
  fact that decided the bucket. Use when the user asks to triage a queue before
  anyone answers.
license: Apache-2.0
metadata:
  category: customer-support
  tags: support, triage
  added: "2026-11-10"
  featured: false
---

# Ticket triage

Put each ticket in one bucket. The bucket is a sorting decision, not a promise to the customer.

## Steps

1. Read each ticket the user pasted. Keep their id. If there is no id, number them in order and say you assigned the number.
2. Choose one bucket: reply (a person can answer from the policy they also pasted), wait (a fact is missing), bug (the ticket describes a broken behavior), or billing (money, a plan, or an invoice).
3. Write the one fact that decided the bucket. If two facts point at two buckets, choose the one that blocks the other and say why.
4. Check that every ticket appears once. Do not drop a ticket because it is angry or short.
5. Do not draft the customer-facing reply in this skill. That is a separate step.

## Example

User: T1 "export button does nothing since Tuesday". T2 "please refund invoice 19" and no refund policy was pasted.

Agent: T1 is bug, because the button stopped working on Tuesday. T2 is wait, because a refund needs a policy and none was pasted. Neither ticket is answered here.

## Boundaries

Do not tell the customer the bug is fixed, and do not approve a refund.
