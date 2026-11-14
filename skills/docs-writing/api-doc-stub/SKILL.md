---
name: api-doc-stub
description: >-
  Documents one HTTP endpoint from its handler: method, path, parameters, status
  codes, and an example call. Use when the user asks for API docs for a route or
  a handler.
license: Apache-2.0
metadata:
  category: docs-writing
  subshelf: repository
  tags: api, docs
  added: "2026-11-07"
  featured: false
---

# API doc stub

Document one endpoint from the handler or route file the user supplies. Do not document a whole API in one pass. Do not invent status codes the handler does not return.

## Steps

1. Read the handler. Note the method, the path, the auth requirement, and the inputs (path, query, body).
2. List each input: name, where it is sent, whether it is required, and what the handler does when it is missing.
3. List the status codes the handler actually returns, with the condition for each.
4. Write one example request and a matching example response using fake values, never real credentials or customer data.
5. Validate the stub by tracing every field and status back to a line in the handler. Delete anything you cannot trace.

## Example

User: Document `GET /invoices/:id`, which returns 200 with the invoice, 404 when the id is unknown, and 401 when the session is missing.

Agent: The stub says GET, path `/invoices/:id`, auth required, path param `id` required. Statuses are 200, 401, and 404. The example uses `id` `inv_100` and a JSON body with `amount_cents`. No 403 is documented because the handler does not return it.

## Boundaries

Do not copy a production payload that contains personal data. Do not guess rate limits.
