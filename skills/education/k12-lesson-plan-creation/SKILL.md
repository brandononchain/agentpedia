---
name: k12-lesson-plan-creation
description: >-
  Writes one K-12 lesson plan from the grade, subject, and objective the teacher
  states. Use when the user asks for a lesson plan, a mini-lesson, or a class
  on a named topic.
license: Apache-2.0
metadata:
  category: education
  subshelf: lessons
  tags: k12, lesson, plan, education
  added: "2026-11-26"
  featured: false
  source: import
  author: Anthropic
  authorUrl: "https://github.com/anthropics"
  authorKind: organization
  curator: Brandon
  upstream: anthropics/k12-teacher-skills
  upstreamCommit: 31fd6dbb0c07cb50bb3ce7f62a4135a393bd0e8c
  upstreamPath: plugin/skills/k12-lesson-plan-creation/SKILL.md
  upstreamLicense: Apache-2.0
  copyright: Copyright Anthropic
---

# K12 lesson plan creation

Do this one job: a lesson plan. Adapted from `anthropics/k12-teacher-skills` at commit `31fd6dbb0c07` (Apache-2.0). Copyright Anthropic

## Steps

1. Confirm the grade, subject, topic, and minutes available. If one of those is missing, ask. Do not guess a grade or a time.
2. Write one plan: the objective in the teacher's words, the sequence of the class, and a check that shows whether that objective was met.
3. Add one student task that practices the same objective. Do not add a second lesson, a unit, or an observation form.
4. If the teacher did not name a standard, write "standard not supplied". Do not invent a standard code.
5. Validate that every activity traces to the objective. A science lesson stays a classroom explanation. Do not add a procedure for making a hazardous substance.

## Example

User: 5th grade math, 40 minutes, objective is to divide a three-digit number by a one-digit number with a remainder.

Agent: One 40-minute plan whose objective is that division, a worked step on the board, and a six-problem student task. The check is three problems the student solves alone. The standard line says "standard not supplied".

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
