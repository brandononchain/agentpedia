---
name: sql-explain-plain
description: >-
  Explains a SQL query in plain language and names full scans, unbounded joins,
  and non-deterministic ordering. Use when the user asks what a query does or
  why it might be slow or surprising.
license: Apache-2.0
metadata:
  category: data-analysis
  tags: sql, data
  added: "2026-11-06"
  featured: false
---

# SQL explain, in plain language

Explain a query to someone who can read the results but should not have to parse the SQL. Name risks you can see in the text. Do not invent a query plan you did not run.

## Steps

1. Read the query. If it is incomplete, ask for the missing statement instead of finishing it with a guess.
2. Write one paragraph: which rows it starts from, how it filters, how it combines other tables, and what it returns.
3. List concrete risks visible in the text: a join with no predicate, a leading wildcard, a function wrapped around a filtered column, `select *` in a nested query, or an `order by` that does not include a unique column.
4. If the user also pasted an `EXPLAIN` plan, tie each risk to a line in that plan. If they did not, label the risks as "visible in the SQL, not measured."
5. Validate the explanation by checking that every table and filter you mentioned appears in the query. Remove anything that does not.

## Example

User: Explain `select * from invoices i join events e on true where i.created_at > now() - interval '7 days'`.

Agent: The query returns every column of invoices created in the last seven days, each paired with every row in `events`, because the join predicate is `true`. Risk, visible in the SQL and not measured: the join is unbounded and will multiply the invoice rows by the size of `events`.

## Boundaries

Do not rewrite the query unless the user asks for a revision. Do not claim an index exists unless the user showed it.
