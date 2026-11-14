---
name: figma-frame-spec
description: >-
  Turns a pasted frame description into a component spec with the tokens and
  states the user named. Use when the user asks to go from a Figma frame, a
  design-system note, or a redline to something an engineer can build.
license: Apache-2.0
metadata:
  category: design-frontend
  subshelf: specs
  tags: figma, design-systems
  added: "2026-11-10"
  featured: false
---

# Frame spec

Write a spec from a frame the user describes. Do not open Figma, and do not invent a token.

## Steps

1. Name the component and the frame they cited. If they pasted a node name, keep it.
2. List the regions in the frame (title, field, action, hint) and the token each region uses, but only tokens they named. An unnamed color is "token not named".
3. List the states they described. A state that is not in the paste is omitted, not assumed.
4. Write the content rules they gave: max length, truncation, what happens when the label wraps. If they gave none, say content rules were not specified.
5. Check the spec by removing any spacing, color, or component that does not appear in their note. Hand back the spec and wait. Do not write the component code unless they ask.

## Example

User: Frame `Card / price`. Title uses `text/title`. The price uses `text/number`. Padding token is `space/3`. There is no error state in the frame. The title wraps to two lines.

Agent: Component follows `Card / price`. Title token `text/title`, price token `text/number`, padding `space/3`. Error is not in the frame, so it is omitted. Content rule: the title wraps to two lines. No code is written.

## Boundaries

Do not fetch a Figma file, and do not substitute a token from memory when they left the name out.
