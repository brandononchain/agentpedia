# What the Dockerfile reader keeps

The script reads one Dockerfile. It does not run `docker build` and it does not pull a base image. The instruction rules are the [Dockerfile reference](https://docs.docker.com/reference/dockerfile/). The note about a non-root user is [Best practices for writing Dockerfiles](https://docs.docker.com/build/building/best-practices/), section USER.

Parser directives are the `# key=value` lines at the top, before a comment, a blank line, or an instruction. The script accepts `syntax`, `check`, and `escape`. `escape` may be `\` or a backtick. The default escape character is `\`. A trailing escape joins the next line. The reported line is the line where the instruction starts.

`FROM` starts a stage. A valid Dockerfile must start with `FROM`. `ARG` is the only instruction that may precede it. Each `FROM` clears state created by previous instructions, so a `USER` in an earlier stage is not copied forward. An optional `AS name` is printed as `name`. `--platform=` is printed as `platform`. Any other flag, including `--reset`, stops the script. The reference says `FROM --reset` is not stable syntax yet. The image token is printed as written. If the tag or digest is omitted, the builder assumes `latest`. The script does not add that tag, and it does not check that an `AS` name exists.

`USER` sets the user, and optionally the group, for the remainder of the current stage. That user is used for later `RUN` instructions and, at runtime, for `ENTRYPOINT` and `CMD`. The last `USER` in the stage is the one still set at the end of the stage. `user_count` is how many `USER` instructions that stage has. The best-practices page says to avoid switching `USER` back and forth frequently.

`user=unset` means this stage contains no `USER` instruction. It does not mean the process runs as root. The base image can set a user, and this file does not show that image. `user_root=yes` only when the token before any `:` is exactly `root`, as in `root` or `root:root`. A numeric token, including `0`, is `user_numeric=yes` and is not labeled root. The best-practices page says that if a service can run without privileges, use `USER` to change to a non-root user, and consider an explicit UID and GID. The script does not turn that advice into a pass or a fail.

`HEALTHCHECK NONE` disables a health check inherited from the base image. `HEALTHCHECK` with options and then `CMD` sets a check. There can be only one `HEALTHCHECK` in a Dockerfile. If more than one is listed, only the last takes effect. The script reports that last form, the count, and the line. It does not run the command, and it does not apply the default intervals from the reference.

The script lists every stage. It does not choose a build target. A heredoc (`<<`), an instruction it does not recognize, a `USER` that is not one token, or a non-`ARG` line before `FROM` stops the script. The stop at 1000000 bytes is the script's own limit.
