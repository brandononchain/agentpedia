---
name: deploy-readiness
description: >-
  Checks a written deploy plan for the rollback, the migration, and the health
  check before anyone ships it. Use when the user asks if a Vercel, AWS, or
  Docker deploy is ready to start.
license: Apache-2.0
metadata:
  category: devops-cloud
  subshelf: deploys
  tags: deploy, cloud
  added: "2026-11-10"
  featured: false
---

# Deploy readiness

Read a plan the user wrote. Say what is present and what is missing. Do not run the deploy.

## Steps

1. Name the target the user named: a Vercel project, an AWS service, a Docker image, or "target not named".
2. Look for four lines in the plan: what is changing, how to tell it worked, how to roll back, and whether a data migration runs first. Mark each present or missing.
3. If a migration is present, check that the plan says it is backward compatible with the version still running. If it does not say, mark that unknown.
4. Validate the note against the plan. Do not add a step the user did not write, and do not claim a preview URL exists unless they pasted it.
5. End with ready, not ready, or ready except for the missing lines. Not ready if rollback or the health check is missing.

## Example

User: Plan: ship the API container to ECS, then watch the /health endpoint. Rollback is the previous task definition. No migration.

Agent: Target is AWS ECS. Changing: the API container. Health check: present. Rollback: present. Migration: none. Ready. The note does not start a deploy.

## Boundaries

Do not push an image, change a setting, or invent a green check from a dashboard you did not see.
