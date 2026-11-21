"""Audit every published skill and agent.

    PYTHONPATH=tools python3 -m audit
    PYTHONPATH=tools python3 -m audit --ci --base origin/main
    PYTHONPATH=tools python3 -m audit --strict

--ci warns on high findings inside the grace period and fails when a new or
changed entry is on hold, or when a high finding has no first-seen date.
--strict fails when any entry is on hold. The nightly workflow uses it.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from audit.engine import audit_directory, public_view  # noqa: E402
from audit.grace import first_seen, load_ledger  # noqa: E402
from audit.models import Finding  # noqa: E402
from certlib import content_digest, today_iso  # noqa: E402


def discover() -> list[tuple[str, str, Path]]:
    found: list[tuple[str, str, Path]] = []
    skills = ROOT / "skills"
    agents = ROOT / "agents"
    if skills.is_dir():
        for manifest in sorted(skills.glob("*/*/SKILL.md")):
            found.append(("skill", manifest.parent.name, manifest.parent))
    if agents.is_dir():
        for manifest in sorted(agents.glob("*/AGENT.md")):
            found.append(("agent", manifest.parent.name, manifest.parent))
    return found


def changed_paths(base: str) -> set[str] | None:
    if not base:
        return None
    completed = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        print(completed.stderr.strip() or f"git diff against {base} failed", file=sys.stderr)
        return None
    return {line.strip() for line in completed.stdout.splitlines() if line.strip()}


def touched(source: Path, paths: set[str] | None) -> bool:
    if paths is None:
        return False
    prefix = source.relative_to(ROOT).as_posix() + "/"
    return any(path == prefix[:-1] or path.startswith(prefix) for path in paths)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Agentpedia static security audit.")
    parser.add_argument("--ci", action="store_true", help="Fail new or changed on-hold entries and missing grace dates.")
    parser.add_argument("--strict", action="store_true", help="Fail if any entry is on hold.")
    parser.add_argument("--base", default="", help="Git base used by --ci to see which entries changed.")
    parser.add_argument("--path", default="", help="Audit one directory instead of the catalog.")
    args = parser.parse_args(argv)

    ledger = load_ledger(ROOT)
    today = today_iso()
    failed = False
    rows: list[tuple[str, dict, list[Finding], Path]] = []

    if args.path:
        directory = Path(args.path)
        if not directory.is_absolute():
            directory = ROOT / directory
        findings, lock, cve = audit_directory(directory)
        view = public_view(
            findings,
            lock=lock,
            content_digest="",
            commit="",
            ledger=ledger,
            entry_id=directory.name,
            today=today,
            cve_lookup=cve,
        )
        rows.append((directory.name, view, findings, directory))
    else:
        for kind, name, directory in discover():
            findings, lock, cve = audit_directory(directory)
            entry_id = f"{kind}-{name}"
            view = public_view(
                findings,
                lock=lock,
                content_digest=content_digest(directory),
                commit="",
                ledger=ledger,
                entry_id=entry_id,
                today=today,
                cve_lookup=cve,
            )
            rows.append((entry_id, view, findings, directory))

    grades = {letter: 0 for letter in "ABCDF"}
    statuses = {"passed": 0, "warning": 0, "on-hold": 0}
    paths = changed_paths(args.base) if args.ci else None
    for entry_id, view, findings, directory in rows:
        grades[view["grade"]] = grades.get(view["grade"], 0) + 1
        statuses[view["status"]] = statuses.get(view["status"], 0) + 1
        print(f"{view['status']:8} {view['grade']} {view['score']:3} {entry_id}")
        for finding in findings:
            print(f"         {finding.rule_id} {finding.severity} {finding.path}:{finding.line} {finding.evidence}")
        if view["status"] == "warning":
            print(f"         warning: {view['summary']}", file=sys.stderr)
        unrecorded = [
            finding
            for finding in findings
            if finding.severity in {"high", "critical"} and first_seen(ledger, entry_id, finding) is None
        ]
        if unrecorded and (args.ci or args.strict):
            failed = True
            print(
                f"error: {entry_id} has a high or critical finding with no first-seen date. "
                "Run python3 tools/build_index.py and commit data/audit-grace.json.",
                file=sys.stderr,
            )
        if view["status"] == "on-hold":
            if args.strict or (args.ci and (paths is None or touched(directory, paths) or args.path)):
                failed = True
                print(f"error: {entry_id} is on hold. {view['summary']}", file=sys.stderr)
            elif args.ci:
                print(f"warning: {entry_id} is on hold and this diff does not change it.", file=sys.stderr)

    print(
        "grades "
        + " ".join(f"{letter}={grades[letter]}" for letter in "ABCDF")
        + " "
        + " ".join(f"{name}={statuses[name]}" for name in ("passed", "warning", "on-hold"))
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
