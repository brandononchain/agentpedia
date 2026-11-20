# Which uses value is which

The script classifies the text of each `uses` value. It does not fetch the action, and it does not open a lockfile. The forms are the ones in [Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) for `jobs.<job_id>.steps[*].uses` and `jobs.<job_id>.uses`. The supply-chain note is [Secure use](https://docs.github.com/en/actions/reference/security/secure-use).

`where=step` is a step action. `where=job` is a reusable workflow. `where=other` is a `uses` key that is neither of those. `job=absent` means the key was not under a job.

Kinds:

- `sha`. The ref after the last `@` is 40 hexadecimal characters. The syntax example of a commit SHA is that length. A shorter hex string stays `movable`. The script does not prove the object exists, and it does not prove the commit is from the action repository rather than a fork. Secure use says to verify that when selecting a SHA.
- `movable`. A ref that is not 40 hexadecimal characters. The syntax page's examples are a major tag, a version tag, and a branch. Secure use says a tag can be moved or deleted.
- `missing-ref`. An `owner/repo` value with no `@`. The syntax page says that omitting a version can break the workflow when the action changes.
- `self-repo`. A value that starts with `$/`. It is the same repository at the running commit. A `$/` value must not include `@`. `suffix=invalid` marks one that does.
- `relative`. A value that starts with `./`. For a step, that is a path in the runner workspace. For a job, `./.github/workflows/{filename}` is a reusable workflow in the same repository, at the same commit as the caller. An `@` on this form is also `suffix=invalid`.
- `docker`. A value that starts with `docker://`. That is a container image, including one whose name contains `@`. It is not a git SHA.
- `expression`. The value contains `${{`. The syntax page says `jobs.<job_id>.uses` cannot contain a context or an expression. The script does not evaluate it.

`prefix=yes` means the ref text starts with `refs/`. For a reusable workflow, the syntax page says prefixes such as `refs/heads` and `refs/tags` are not allowed. The script still reports the kind, and it does not rewrite the ref.

Secure use says the strongest measure is a workflow dependency lockfile, which records the commit for every action, including transitive ones, and supersedes SHA pinning for a repository that adopts it. For a repository that cannot adopt a lockfile, that page says to pin actions to a full-length commit SHA. The same page says the principles apply to third-party reusable workflows. This script does not look for the lockfile. A count of `sha` is not a claim that a lockfile exists, and `movable` is not a claim that the file was compromised.

The script stops at 1000000 bytes. That limit is the script's, not GitHub's. A tab used as indentation, a `---` document marker, a `uses` value with no one-line scalar, or extra text that is not an expression stops the script. A `|` or `>` block is not searched, so a `uses` string inside a `run` script is not a row.
