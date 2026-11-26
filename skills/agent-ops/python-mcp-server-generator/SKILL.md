---
name: python-mcp-server-generator
description: >-
  Drafts a Python MCP server with typed tools and an in-memory test. Use when
  the user wants a new MCP server in Python for tools they name. The user
  installs the SDK.
license: MIT
metadata:
  category: agent-ops
  subshelf: connectors
  tags: python, mcp, server, agent
  added: "2026-11-26"
  featured: false
  source: import
  author: "GitHub, Inc."
  authorUrl: "https://github.com/github"
  authorKind: organization
  curator: Brandon
  upstream: github/awesome-copilot
  upstreamCommit: 93fc8b9ee3ef56b9b5e7261e6ce92d314cb2c1cf
  upstreamPath: skills/python-mcp-server-generator/SKILL.md
  upstreamLicense: MIT
  copyright: "Copyright GitHub, Inc."
---

# Python mcp server generator

Do this one job: a Python MCP server draft. Adapted from `github/awesome-copilot` at commit `93fc8b9ee3ef` (MIT). Copyright GitHub, Inc.

## Steps

1. Confirm each tool the user wants, with its inputs, its output, and whether it only reads. If a tool is missing those, ask. Do not add a tool they did not name.
2. Draft `server.py` in the reply: one MCP server object, one typed function per tool, a docstring, and an error for a bad input. Mark a read-only tool as read-only.
3. Draft one in-memory test per tool in the reply. The test calls the tool and checks the returned value. It does not open a port.
4. Tell the user to install the MCP Python SDK and the test runner themselves. Do not run an installer and do not phone a registry.
5. Validate that every drafted tool matches a request, and that a tool which writes or deletes is not marked read-only.

## Example

User: One tool, divide, two floats, returns a float. It must fail when the divisor is zero. It only computes.

Agent: A server draft with a divide tool that raises when the divisor is zero, and a test that calls divide(6, 3) and expects 2. The reply says the user installs the SDK. No install command is run.

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
