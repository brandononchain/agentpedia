---
name: k12-lesson-prep
description: >-
  Writes a teacher-only prep note for a K-12 lesson the user already has. Use
  when the user asks to prepare, internalize, or get ready to teach that lesson.
license: Apache-2.0
metadata:
  category: education
  subshelf: lessons
  tags: k12, lesson, prep, education
  added: "2026-11-27"
  featured: false
  source: import
  author: Anthropic
  authorUrl: "https://github.com/anthropics"
  authorKind: organization
  curator: Brandon
  upstream: anthropics/k12-teacher-skills
  upstreamCommit: 31fd6dbb0c07cb50bb3ce7f62a4135a393bd0e8c
  upstreamPath: plugin/skills/k12-lesson-prep/SKILL.md
  upstreamLicense: Apache-2.0
  copyright: "Copyright 2026 Anthropic, PBC. Copyright 2026 Learning Commons."
---

# K12 lesson prep

Do this one job: a prep note for a lesson the teacher already has. Adapted from `anthropics/k12-teacher-skills` at commit `31fd6dbb0c07` (Apache-2.0). Copyright 2026 Anthropic, PBC. Copyright 2026 Learning Commons.

## Steps

1. Read the lesson the user supplied. If the message has only a title, ask for the lesson text. Do not prep from a guess.
2. Name the key student task in the lesson's own words.
3. Ask the teacher to try that task and say where an almost-right answer would go wrong. Wait for the answer.
4. After they answer, say what the task is built to reveal. If they have a content fact wrong, say so plainly.
5. Write a prep note of at most 300 words. Walk the lesson's parts in teaching order. Put each finding under the part it belongs to.
6. Check the note. Every claim points at the lesson or at something the teacher said. Leave anything else labeled unknown. Do not add a quiz, a grade, or a student-facing page.

## Example

User: Tomorrow's grade 4 lesson asks students to compare 1/2 and 3/4 with fraction strips. I think 3/4 is larger because 3 is bigger than 1. Help me get ready to teach it.

Agent: The key task is comparing 1/2 and 3/4 with strips, not comparing the numerators. 3/4 is larger, and the reason is the size of the pieces, not that 3 is bigger than 1. Prep note: opening — students build both strips; the almost-right answer treats the numerator as the whole comparison. Close — students say which strip is longer and why the pieces are different sizes. No quiz added.

## Boundaries

Do not publish the note, send it, or file it anywhere. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent a standard, a timing, or a student the user did not mention.
