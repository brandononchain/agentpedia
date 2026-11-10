# What stays in the skill body

Keep the entrypoint short enough to load on every run.

- The description: the job, and when to use the skill, in third person.
- The numbered steps an agent follows every time.
- One example.
- The validation check and the limits.

# What moves to references

Move a section out when it is long or only needed on some runs.

- A full flag table from CLI help.
- An endpoint list or a status-code table.
- A long sample payload.
- Notes that apply to one version only.

Write that material into `references/` and link it from `SKILL.md`. Do not link a file that was not created. If the source is already short, skip the extra file and say why.
