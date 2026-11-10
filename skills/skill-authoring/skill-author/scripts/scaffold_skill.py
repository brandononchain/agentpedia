#!/usr/bin/env python3
"""Create a skill folder with frontmatter that matches the Skilldex bar."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

TEMPLATE = """---
name: {name}
description: >-
  {description}
license: Apache-2.0
metadata:
  category: {category}
  tags: {tags}
  added: "{added}"
  featured: "false"
---

# {title}

Say what finished work looks like, and what this skill will not do.

## Steps

1. Confirm the input and the output.
2. Do the work from the files and facts the user supplied.
3. Validate the result against a check you can point at, then show the work.

## Example

User: Replace this line with a realistic request.

Agent: Show a short concrete result. Replace this line before the skill ships.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("category")
    parser.add_argument("name")
    parser.add_argument("description")
    parser.add_argument("--tags", default="draft")
    parser.add_argument("--root", default="skills")
    args = parser.parse_args()
    if "use when" not in args.description.lower() and "when " not in args.description.lower():
        raise SystemExit("description must say when to use the skill")
    folder = Path(args.root) / args.category / args.name
    folder.mkdir(parents=True, exist_ok=False)
    title = args.name.replace("-", " ").capitalize()
    text = TEMPLATE.format(
        name=args.name,
        description=args.description.strip(),
        category=args.category,
        tags=args.tags,
        added=date.today().isoformat(),
        title=title,
    )
    path = folder / "SKILL.md"
    path.write_text(text, encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
