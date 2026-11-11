---
name: trace-debug-note
description: >-
  Reads a pasted agent trace and names the first step that diverged from the
  job. Use when the user asks to debug or monitor another agent's run from a
  log they already captured.
license: Apache-2.0
metadata:
  category: agent-ops
  tags: debugging, traces
  added: "2026-11-10"
  featured: false
---

# Trace debug note

Find the first wrong step in a trace the user pasted. Do not re-run the agent.

## Steps

1. Restate the job the user said the agent was given. If the trace does not include the job, use the job they typed beside it and say the trace itself omitted the job.
2. Walk the steps in order. The failure is the first step that does something else: calls a tool the job forbade, invents a fact, or stops before the observable result.
3. Quote that step. Note the tool name if one was called. Do not quote a secret if the trace contains one; say "secret redacted" and keep the step number.
4. Check that later steps are described as consequences, not as a second root cause, unless a later step fails for an unrelated reason. Say which.
5. Do not claim the next run will pass. Say what to change in the case or the instruction, as a hypothesis.

## Example

User: Job: sum the invoice and do not pay. Step 1 sums to 10. Step 2 calls `send_payment`.

Agent: The first divergence is step 2, which calls `send_payment` after a job that forbade payment. Step 1 matched the sum. The note does not say a retry would pass.

## Boundaries

Do not rerun the agent, and do not paste a secret from the trace into the note.
