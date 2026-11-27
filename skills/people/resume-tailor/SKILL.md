---
name: resume-tailor
description: >-
  Rewrites a resume the user pasted so it matches a job description they also
  pasted, without adding experience. Use when the user asks to tailor a resume
  or a CV to a role.
license: MIT
metadata:
  category: people
  subshelf: roles
  tags: resume, tailor, people
  added: "2026-11-27"
  featured: false
  source: import
  author: Claude Office Skills Contributors
  authorUrl: "https://github.com/claude-office-skills"
  authorKind: organization
  curator: Brandon
  upstream: claude-office-skills/skills
  upstreamCommit: 9c4c7d5cd2813a8936bf2c9fdb174ea883b85a11
  upstreamPath: resume-tailor/SKILL.md
  upstreamLicense: MIT
  copyright: Copyright (c) 2026 Claude Office Skills Contributors
---

# Resume tailor

Do this one job: a resume draft that uses only lines the user already wrote. Adapted from `claude-office-skills/skills` at commit `9c4c7d5cd281` (MIT). Copyright (c) 2026 Claude Office Skills Contributors

## Steps

1. Read the resume and the job description. If either is missing, ask. Do not call a document tool.
2. List the requirements in the job description. Mark each as shown in the resume, partial, or absent.
3. Reorder and reword only bullets that already appear in the resume, so the matching ones lead. Keep employers, dates, and titles unchanged.
4. Use a word from the job description only when the resume already shows that work. Do not add a metric, a tool, or a job that is not in the resume.
5. Check the draft against the source resume. Every claim still has a source bullet. List the requirements that were left out.

## Example

User: Resume says "Wrote the weekly status note for five engineers, 2023-2024, Northwind." The job asks for "stakeholder updates" and "Python." Tailor it.

Agent: Shown — stakeholder updates, from the weekly status note. Absent — Python, not in the resume, so it is not added. Draft bullet, same employer and dates: "Wrote the weekly status note for five engineers." No new metric.

## Boundaries

Do not submit the resume or contact an employer. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent employment, dates, or results.
