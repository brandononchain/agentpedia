"""Pick the shelf for the next daily entry.

Every directory under skills/ that has a category.json is in the rotation,
in alphabetical id order. The calendar day selects one shelf, and a run of
days equal to the shelf count visits each shelf once.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path


def shelf_ids(skills_root: Path) -> list[str]:
    if not skills_root.is_dir():
        return []
    names = []
    for path in sorted(skills_root.iterdir()):
        if path.is_dir() and (path / "category.json").is_file():
            names.append(path.name)
    return names


def next_shelf(shelves: list[str], on: date) -> str:
    if not shelves:
        raise ValueError("no shelves to rotate")
    return shelves[on.toordinal() % len(shelves)]
