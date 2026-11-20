# Which permissions key counts

The script reads `permissions` keys in one workflow file. The names, the access levels, and the calculation order are the workflow syntax page, section `permissions` and section `jobs.<job_id>.permissions`: [Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax).

A top-level key applies to the jobs in the file. A key on a job is that job's key. `skipped_permissions` counts a `permissions` key that is neither of those, including one nested under a step. That key is not reported as a token scope.

Forms the syntax page shows:

- `read-all` and `write-all`.
- `{}`, printed as `form=none`, which disables every available permission.
- A map of scope names. If any scope is set, every scope that is not named in that map is `none`. The script prints `unspecified=none` only for a map. It does not expand `read-all` or `write-all` into names.

The syntax example allows these scopes and no others. `write` includes `read` on that page. The script prints the token that was written. It does not add `read` beside `write`.

| Scope | Access the example allows |
| --- | --- |
| `actions` | `read`, `write`, `none` |
| `artifact-metadata` | `read`, `write`, `none` |
| `attestations` | `read`, `write`, `none` |
| `checks` | `read`, `write`, `none` |
| `code-quality` | `read`, `write`, `none` |
| `contents` | `read`, `write`, `none` |
| `copilot-requests` | `write`, `none` |
| `deployments` | `read`, `write`, `none` |
| `id-token` | `write`, `none` |
| `issues` | `read`, `write`, `none` |
| `discussions` | `read`, `write`, `none` |
| `packages` | `read`, `write`, `none` |
| `pages` | `read`, `write`, `none` |
| `pull-requests` | `read`, `write`, `none` |
| `security-events` | `read`, `write`, `none` |
| `statuses` | `read`, `write`, `none` |
| `vulnerability-alerts` | `read`, `none` |

`reason=unknown` is a name that is not in that example. `reason=level` is an access token the example does not allow for that name, including `id-token: read`, `copilot-requests: read`, and `vulnerability-alerts: write`. The page also says that when `read-all` or `write-all` is used, `vulnerability-alerts` is included as `read`. The script does not add that row itself.

`form=flow`, `form=empty`, and `form=scalar` are not read as scopes. A one-line `{contents: read}` is `flow`. An empty block under `permissions:` is `empty`. A word other than `read-all`, `write-all`, or `{}` is `scalar`.

`duplicate=` names a scope that appears twice in one map. `duplicate_workflow=yes` means two top-level keys. `duplicate_job=yes` means two jobs share an id. The script prints the lines and does not pick a winner. `ok=no` when any of those, or an unknown scope, or a level the example does not allow, is present.

`job_form=absent` means that job has no `permissions` key. The top-level key is then the one the file sets for it. The script does not copy those scopes onto the job. When the job key is a map, omitted scopes in that map are `none`, and the workflow map is not merged in.

The page says the token starts from the enterprise, organization, or repository default, then the workflow key, then the job key. This file does not contain that default. `workflow_form=absent` does not mean the token has no access.

Two further rules are on the same page, and the script does not apply them, because a file does not say which event ran or how the repository is configured:

- A workflow triggered by `pull_request_target` is granted read/write repository permission, including from a public fork. `pull_request_target=yes` means that event name appears under `on`. The scopes are not rewritten.
- For a pull request event other than `pull_request_target` from a fork, when the setting to send write tokens is not selected, write permissions are changed to read. The script leaves `write` as written.

The script stops at 1000000 bytes. That limit is the script's, not GitHub's. A tab indent, a `---` document marker, or a `permissions` map that is not a flat list of `scope: access` lines stops the script. Text inside a `|` or `>` block is not a key.
