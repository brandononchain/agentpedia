# Review rubric

Use this order. Stop adding notes once the blockers are clear.

1. Correctness: does the change do what the description says, on the inputs that matter?
2. Data loss: deletes, overwrites, migrations, and exports that skip a filter.
3. Auth: missing checks, trust of client-supplied ids, and broader permissions than before.
4. Concurrency: double submits, lost updates, and jobs that assume a single worker.
5. Tests: the behavior a reviewer would be afraid to change without a failing test.

A finding without a file and a behavior is not a finding.
