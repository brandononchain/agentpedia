---
name: release-notes-editor
description: >-
  Rewrites internal changelog lines into release notes a user of the product can
  act on. Use when the user asks for release notes, a launch note, or a plain-
  language what-changed.
license: Apache-2.0
metadata:
  category: docs-writing
  tags: release, docs
  added: "2026-11-07"
  featured: false
---

# Release notes editor

Turn internal notes into release notes for people who use the product. Cut tickets, class names, and refactors they cannot see.

## Steps

1. Read the changelog or commit notes and the audience (end user, admin, or integrator). Ask which audience if it is missing.
2. Keep items a person in that audience can notice or must act on. Drop pure refactors unless behavior changed.
3. Rewrite each item as what changed and, when needed, what the reader should do.
4. Put breaking changes and required actions above everything else.
5. Validate the notes against the source list. Every sentence must map to a source line. Do not add a feature that was not in the source.

## Example

User: Rewrite for end users. Source: "Added CSV export on the invoice list. Fixed export so deleted invoices are excluded. Renamed InvoiceRow to InvoiceListItem."

Agent: You can export the invoice list as CSV. Deleted invoices are left out of the export. The rename is omitted because users cannot see it.

## Boundaries

Do not promise a date or a fix that is not in the source. Do not leave internal codenames in the final notes.
