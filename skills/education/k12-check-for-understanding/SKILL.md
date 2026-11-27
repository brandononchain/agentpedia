---
name: k12-check-for-understanding
description: >-
  Writes one to three math items that show whether students understood one
  idea, plus a teacher note for each wrong answer. Use when the user asks for a
  check for understanding, a formative check, or an exit ticket.
license: Apache-2.0
metadata:
  category: education
  subshelf: assessment
  tags: k12, formative, math, education
  added: "2026-11-27"
  featured: false
  source: import
  author: Anthropic
  authorUrl: "https://github.com/anthropics"
  authorKind: organization
  curator: Brandon
  upstream: anthropics/k12-teacher-skills
  upstreamCommit: 31fd6dbb0c07cb50bb3ce7f62a4135a393bd0e8c
  upstreamPath: plugin/skills/k12-check-for-understanding/SKILL.md
  upstreamLicense: Apache-2.0
  copyright: "Copyright 2026 Anthropic, PBC. Copyright 2026 Learning Commons."
---

# K12 check for understanding

Do this one job: a short math check and a teacher key for reading the answers. Adapted from `anthropics/k12-teacher-skills` at commit `31fd6dbb0c07` (Apache-2.0). Copyright 2026 Anthropic, PBC. Copyright 2026 Learning Commons.

## Steps

1. Confirm the grade, the topic or standard, and the one idea to check. If any of those is missing, ask. Do not invent a standard code.
2. Ask which misconception the teacher has actually seen. If they have not named one, mark the wrong answers as unconfirmed.
3. Write one to three items on that idea only. Each wrong choice is a specific wrong step, not a random number.
4. For each choice, write the next move the teacher can make in a few minutes. Do not assign a score or a grade.
5. Check the draft. The student-facing text has no answer key. Every item stays on the confirmed idea. No sentence copies a page the user did not paste.

## Example

User: Grade 6. We just divided fractions. I want to see who flips the second fraction. The wrong move I keep seeing is dividing the numerators and the denominators straight across.

Agent: One item. Compute 3/4 divided by 2/5. Choices: 15/8 (flip the second fraction), 3/10 (straight across, the misconception you named), 6/20 (multiply without flipping). Teacher note: 3/10 means they divided straight across, so the next move is one strip diagram of 3/4 split into groups of 2/5. No score.

## Boundaries

Do not publish the check or turn it into a graded test. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent a standard, a rubric point, or a student name.
