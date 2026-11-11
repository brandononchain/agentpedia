---
name: ci-log-triage
description: >-
  Names the first failing step in a pasted CI log and separates the error line
  from noise around it. Use when the user asks why a GitHub Actions, Vercel, or
  other build log failed.
license: Apache-2.0
metadata:
  category: devops-cloud
  tags: ci, logs
  added: "2026-11-10"
  featured: false
---

# CI log triage

Find the failure in a log the user pasted. Quote it. Do not rerun the job.

## Steps

1. Identify the job name and the step name if the log has them. If the paste is a fragment, say it is a fragment.
2. Find the earliest line that states a failure: a non-zero exit, an error, a failed test, or a cancelled step. Quote that line and the step it belongs to.
3. List up to three lines above it that name a file, a command, or a test. Ignore timestamps and progress percents unless they are the only context.
4. Check that the quoted failure appears in the paste. If two steps failed, name both and say which one is earlier.
5. Say what a person could look at next, as a question, not as a command you ran. Do not claim the build is fixed.

## Example

User: The log says "Run npm test" then "FAIL src/bill.test.js" then "Error: expected 3 received 4" and later "Post checkout".

Agent: The job name is not in the paste, so this is a fragment. The first failure is in "Run npm test": `FAIL src/bill.test.js` and `expected 3 received 4`. "Post checkout" is after the failure and is not the cause. Next question: which assertion in that test expected 3.

## Boundaries

Do not rerun CI, and do not treat a green line after the failure as proof the failure was retried successfully unless the log says so.
