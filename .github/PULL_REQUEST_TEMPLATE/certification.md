## Certification submission

- [ ] Skill or agent added under `skills/`, `agents/`, or `submissions/incoming/`
- [ ] `SKILL.md` or `AGENT.md` follows the lint bar in CONTRIBUTING.md
- [ ] Optional: `certs/checks/<id>.json` with an install probe and at least one eval

The Certify workflow lints changed skills and runs declared checks with a read-only token. A separate workflow on the default branch comments with that report. It does not run pull-request code. Recording `certs/results/` is a maintainer dispatch of Certify record on the default branch, or a local `tools/verify_checks.py --write`. A pull-request label cannot write those files.

Listed is issued by the catalog build when the score is 100. Verified requires that recorded run. Certified requires a human `review` object in `certs/records/<id>.json`.
