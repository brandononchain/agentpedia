"""skills-lock v2 content hash.

Compatible with vercel-labs/skills `hashSkillFiles` (lockfile `computedHash`):
paths sorted by UTF-8 bytes, each file framed as path NUL length NUL content,
CRLF normalized to LF in text files. Excludes metadata.json and the directories
.git, __pycache__, and __pypackages__. Symlinks that leave the folder are omitted.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

EXCLUDE_FILES = {"metadata.json"}
EXCLUDE_DIRS = {".git", "__pycache__", "__pypackages__"}


def is_excluded(name: str, is_directory: bool = False) -> bool:
    if name in EXCLUDE_FILES:
        return True
    if is_directory and name in EXCLUDE_DIRS:
        return True
    return False


def _normalize(content: bytes) -> bytes:
    if b"\0" in content or b"\r\n" not in content:
        return content
    return content.replace(b"\r\n", b"\n")


def hash_skill_files(files: list[tuple[str, bytes]]) -> str:
    entries = []
    for path, content in files:
        rel = path.replace("\\", "/")
        entries.append((rel.encode("utf-8"), _normalize(content)))
    entries.sort(key=lambda item: item[0])
    hasher = hashlib.sha256()
    for path, content in entries:
        hasher.update(path)
        hasher.update(b"\0")
        hasher.update(str(len(content)).encode("ascii"))
        hasher.update(b"\0")
        hasher.update(content)
    return hasher.hexdigest()


def _inside(root: Path, target: Path) -> bool:
    try:
        target.relative_to(root)
    except ValueError:
        return False
    return True


def collect_skill_files(directory: Path) -> list[tuple[str, bytes]]:
    root = directory.resolve()
    files: list[tuple[str, bytes]] = []

    def walk(current: Path, prefix: str) -> None:
        try:
            children = sorted(current.iterdir(), key=lambda item: item.name.encode("utf-8"))
        except OSError:
            return
        for entry in children:
            if is_excluded(entry.name, entry.is_dir() and not entry.is_symlink()):
                continue
            rel = f"{prefix}{entry.name}"
            if entry.is_symlink():
                try:
                    target = entry.resolve(strict=True)
                except OSError:
                    continue
                if not _inside(root, target):
                    continue
                if target.is_dir():
                    if is_excluded(entry.name, True):
                        continue
                    walk(entry, f"{rel}/")
                elif target.is_file():
                    files.append((rel, target.read_bytes()))
                continue
            if entry.is_dir():
                walk(entry, f"{rel}/")
            elif entry.is_file():
                files.append((rel, entry.read_bytes()))

    if directory.is_dir():
        walk(directory, "")
    return files


def lock_hash(directory: Path) -> str:
    return hash_skill_files(collect_skill_files(directory))
