from __future__ import annotations

from pathlib import Path

SKIP_DIRS = {".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__", ".tox"}


def find_skill_file(directory: Path) -> Path | None:
    exact = directory / "SKILL.md"
    if exact.is_file():
        return exact
    matches = [p for p in directory.iterdir() if p.is_file() and p.name.lower() == "skill.md"]
    if not matches:
        return None
    # Prefer exact case, otherwise the first match (e.g. skill.md)
    for candidate in matches:
        if candidate.name == "SKILL.md":
            return candidate
    return sorted(matches, key=lambda p: p.name)[0]


def discover(path: Path) -> list[Path]:
    """Return SKILL.md files for a file, a skill folder, or a tree of skill folders."""
    path = path.expanduser()
    if not path.exists():
        raise FileNotFoundError(str(path))
    if path.is_file():
        return [path]
    top = find_skill_file(path)
    if top is not None:
        return [top]
    found: list[Path] = []
    for dirpath, dirnames, filenames in _walk(path):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        skill_names = [name for name in filenames if name.lower() == "skill.md"]
        if "SKILL.md" in skill_names:
            found.append(dirpath / "SKILL.md")
        else:
            for name in skill_names:
                found.append(dirpath / name)
    return sorted(found, key=lambda p: str(p).lower())


def _walk(root: Path):
    # pathlib-friendly os.walk
    import os

    for dirpath, dirnames, filenames in os.walk(root):
        yield Path(dirpath), dirnames, filenames
