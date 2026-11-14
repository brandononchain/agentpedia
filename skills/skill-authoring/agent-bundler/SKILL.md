---
name: agent-bundler
description: >-
  Composes an agent manifest that bundles existing skills, names the connectors
  it needs, and includes sample prompts. Use when the user asks to define an
  agent or to bundle skills into one workflow.
license: Apache-2.0
metadata:
  category: skill-authoring
  subshelf: bundles
  tags: agents, skills
  added: "2026-11-10"
  featured: false
---

# Agent bundler

Define an agent as a small bundle of skills that already exist, plus the connectors it needs and three sample prompts. Do not invent skills to fill a gap. Point at the missing skill instead.

## Steps

1. Write the agent's job in one sentence. If the job needs unrelated workflows, split it into two agents and say why.
2. Choose skills from the catalog the user has. For each skill, write when the agent should reach for it.
3. List connectors (MCP or other tools) the skills need. Mark each as required or optional. If a skill can run from pasted input, say so.
4. Write three sample prompts a person could give the agent on the first day. Each prompt must be answerable with the bundled skills.
5. Validate the manifest: every skill name exists, every prompt maps to a skill, and the description says when to use the agent. Do not claim a connector is connected. Check the file by reading it back against the skill list.

## Example

User: Bundle the journal, the risk sizer, and the session plan into a trading agent. MetaTrader is optional.

Agent: The manifest names those three skills, marks MetaTrader as optional because numbers can be pasted, and includes a prompt that asks for a journal entry from a pasted ticket. It does not add a signal skill, because none was requested and none is in the bundle. The description says to use the agent when the user wants the trading workflow rather than one skill.

## Boundaries

Do not bundle a skill that contradicts another (one skill that forbids orders, and a new instruction that places them). The stricter safety rule wins. Write that rule into the agent.
