"""Lint changed skills and run declared checks. Used by the certify workflow.

Writes a Markdown report. Exits 1 when lint finds an error or a warning, or a
check fails. --write records passing runs for manifests that this diff touched.
A harness change re-runs every manifest, because old results go re-check pending.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "skill-lint"))

from skill_lint.cli import lint_path  # noqa: E402
from skill_lint.report import render_text  # noqa: E402
from verify_checks import execute, write_result  # noqa: E402
from certlib import CertError  # noqa: E402


def changed_files(base: str) -> list[str]:
    completed = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.stderr.strip() or f"git diff against {base} failed")
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def skill_dirs(files: list[str]) -> list[Path]:
    found: list[Path] = []
    seen: set[Path] = set()
    for name in files:
        path = ROOT / name
        parts = Path(name).parts
        candidates: list[Path] = []
        if len(parts) >= 3 and parts[0] == "skills":
            candidates.append(ROOT / parts[0] / parts[1] / parts[2])
        if parts[0] == "submissions":
            cursor = path if path.is_dir() else path.parent
            while cursor != ROOT and ROOT in cursor.parents:
                if (cursor / "SKILL.md").is_file():
                    candidates.append(cursor)
                    break
                cursor = cursor.parent
        for candidate in candidates:
            if candidate in seen or not (candidate / "SKILL.md").is_file():
                continue
            seen.add(candidate)
            found.append(candidate)
    return found


def check_ids(files: list[str], harness_changed: bool) -> list[str]:
    if harness_changed:
        return sorted(path.stem for path in (ROOT / "certs" / "checks").glob("*.json"))
    identifiers = []
    for name in files:
        path = Path(name)
        if path.parts[:2] == ("certs", "checks") and path.suffix == ".json":
            identifiers.append(path.stem)
    return identifiers


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report lint and check results for a certification pull request.")
    parser.add_argument("--base", default="origin/main")
    parser.add_argument("--write", action="store_true", help="Record passing runs for manifests this diff touched.")
    parser.add_argument("--out", default="", help="Also write the Markdown report to this path.")
    args = parser.parse_args(argv)

    files = changed_files(args.base)
    harness_changed = "tools/verify_checks.py" in files
    folders = skill_dirs(files)
    identifiers = check_ids(files, harness_changed)

    lines = ["## Certification report", ""]
    failed = False

    if not folders and not identifiers:
        lines.append("No skill folders or check manifests changed against " + args.base + ".")
    if folders:
        lines.append("### Lint")
        lines.append("")
        for folder in folders:
            result = lint_path(folder)
            relative = folder.relative_to(ROOT).as_posix()
            problems = result.error_count + result.warn_count
            lines.append(f"- `{relative}`: {result.error_count} error(s), {result.warn_count} warning(s), {result.info_count} note(s)")
            if problems:
                failed = True
                lines.append("")
                lines.append("```")
                lines.append(render_text(result, color=False).rstrip())
                lines.append("```")
                lines.append("")
        lines.append("")
    if identifiers:
        lines.append("### Checks")
        lines.append("")
        if harness_changed:
            lines.append("The check harness changed, so every manifest was run. Existing Verified results go re-check pending until a new result is recorded.")
            lines.append("")
        for identifier in identifiers:
            manifest = ROOT / "certs" / "checks" / f"{identifier}.json"
            if not manifest.is_file():
                lines.append(f"- `{identifier}`: manifest missing")
                failed = True
                continue
            try:
                result = execute(ROOT, manifest)
            except (CertError, ValueError) as exc:
                lines.append(f"- `{identifier}`: {exc}")
                failed = True
                continue
            lines.append(f"- `{identifier}`: {'passed' if result['ok'] else 'failed'}")
            for check in result["checks"]:
                lines.append(f"  - {check['kind']} `{check['id']}` exit {check['exitCode']} ({'ok' if check['ok'] else 'failed'})")
                if not check["ok"] and check.get("stdout"):
                    lines.append("    " + check["stdout"].strip().replace("\n", "\n    "))
            if not result["ok"]:
                failed = True
                continue
            if args.write:
                try:
                    write_result(ROOT, result)
                except CertError as exc:
                    lines.append(f"  - not recorded: {exc}")
                    failed = True
                    continue
                lines.append(f"  - wrote `certs/results/{identifier}.json`")
        lines.append("")

    if failed:
        lines.append("The pull request is not ready to record a certificate.")
    else:
        lines.append("Lint and checks reported here passed. Listed is recorded by the catalog build. Verified is recorded only when this workflow is asked to write results.")
    report = "\n".join(lines).rstrip() + "\n"
    sys.stdout.write(report)
    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
