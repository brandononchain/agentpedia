## Certification submission

- [ ] Skill or agent added under `skills/`, `agents/`, or `submissions/incoming/`
- [ ] `SKILL.md` or `AGENT.md` follows the lint bar in CONTRIBUTING.md
- [ ] Optional: `certs/checks/<id>.json` with an install probe and at least one eval

The certify workflow comments with the lint and check result. It writes `certs/results/` only when a maintainer runs the workflow with “write results” or adds the `record-checks` label.

Listed is issued by the catalog build when the score is 100. Verified requires that recorded run. Certified requires a human `review` object in `certs/records/<id>.json`.
