---
name: test-gap-finder
description: >-
  Maps a code change to existing tests and lists behaviors that nothing covers.
  Use when the user asks which tests are missing, what to test next, or where a
  diff is untested.
license: Apache-2.0
metadata:
  category: dev-tools
  subshelf: tests
  tags: testing, review
  added: "2026-11-08"
  featured: false
---

# Test gap finder

Find missing tests for a change. Propose the smallest set that would fail if the new behavior broke. Do not generate a large speculative suite.

## Steps

1. Read the diff and locate the functions, branches, and error paths that changed.
2. Find tests that already call that code. Name the file. If none exist, say so.
3. List gaps as behaviors, not as file names: the input, the expected result, and why this change makes it worth a test.
4. Mark each gap as now (this PR) or later (pre-existing, not introduced here).
5. Validate the list by pointing at the branch or condition in the diff. Drop any gap the current tests already cover.

## Example

User: What is untested in the retry helper diff?

Agent: Now — a 429 followed by a 200 should return the success response and record three attempts. Now — a non-retryable 400 should fail on the first attempt. Later — the helper still has no test for a clock that jumps backward. Existing coverage: `retry.test.ts` only covers the happy path with no status code.

## Boundaries

Do not mark a change fully tested because a nearby file has tests. Do not invent a test framework the repo does not use; match the runner already in the project.
