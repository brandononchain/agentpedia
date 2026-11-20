---
name: dockerfile-stage-user
description: >-
  Reports the last USER in each Dockerfile stage and the last HEALTHCHECK in
  the file. Use when the user asks which user or health check a Dockerfile
  sets before a build.
license: Apache-2.0
compatibility: >-
  Python 3.10 or newer for scripts/read_stages.py. Reads one local Dockerfile.
  No network and no extra packages.
metadata:
  category: devops-cloud
  subshelf: deploys
  tags: docker, image
  added: "2026-11-20"
  featured: false
---

# Dockerfile stage user

Report the last `USER` in each stage and the last `HEALTHCHECK` in the file. Use [scripts/read_stages.py](scripts/read_stages.py). Which instruction wins, and what unset does not mean, is in [references/stage-rules.md](references/stage-rules.md).

## Steps

1. Take one Dockerfile. If the user has several, ask which file. Do not run `docker build`, and do not pull the base image.
2. Run `python3 scripts/read_stages.py` on that file. The fixture is [assets/Dockerfile](assets/Dockerfile), and it is not the user's image.
3. For each stage, keep `from_line`, `image`, `name`, `platform`, `user`, `user_line`, `user_count`, `user_root`, and `user_numeric` as printed. Then keep `healthcheck`, `healthcheck_count`, and `healthcheck_line`.
4. `user=unset` means that stage has no `USER` instruction. Do not call the stage root. `user_root=yes` only when the last user token is `root`. A numeric token, including `0`, stays `user_numeric=yes`.
5. Check the printed user against that line, or against the stage when the user is unset. Check the health-check line the same way. When more than one `HEALTHCHECK` is present, the last one is the one the reference says takes effect.
6. If the script stops, quote the message and do not fill in the missing stage. Do not add `:latest` to an image that omitted a tag.

## Example

User: Which user and health check does `assets/Dockerfile` set? Do not build the image.

Agent: Runs `python3 scripts/read_stages.py assets/Dockerfile`.

```
ok=yes
stages=2
stage=0
from_line=3
image=ubuntu:24.04
name=base
platform=absent
user=unset
user_line=absent
user_count=0
user_root=no
user_numeric=no
stage=1
from_line=6
image=base
name=absent
platform=absent
user=app
user_line=7
user_count=1
user_root=no
user_numeric=no
healthcheck=cmd
healthcheck_count=1
healthcheck_line=8
```

Stage 0 is `ubuntu:24.04` named `base`, and this file sets no `USER` there. That is unset, not a claim that the base image runs as root. Stage 1 starts `FROM base`, then `USER app` on line 7. The only `HEALTHCHECK` starts on line 8 and is a `CMD` check, so it is the one that would take effect. The image is not built.

## Boundaries

Do not build, push, or run the image. Do not invent a user from a base image this file does not contain. A deploy plan that names Docker but has no Dockerfile is deploy-readiness. This skill does not decide that the deploy is ready.
