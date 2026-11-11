#!/usr/bin/env python3
"""Run declared install and eval checks in a scrubbed subprocess.

The static site build does not run this harness. A passing run is real only
after this program writes certs/results/<id>.json. Hand-written result files
are rejected by the publisher unless producer is agentpedia-verify-checks
and the digest still matches; CI and this CLI are the writers.

The sandbox is a subprocess: shell is off, the working directory is the
entry, the environment is an allowlist, and the process has a timeout.
It is not a virtual machine and it is not a security audit.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from certlib import (  # noqa: E402
    CHECKS_DIR,
    RESULTS_DIR,
    CertError,
    content_digest,
    git_commit,
    load_json,
    load_records,
    save_record,
    sha256_file,
)

MANIFEST_SCHEMA = "agentpedia.check-manifest.v1"
RESULT_SCHEMA = "agentpedia.check-result.v1"
PRODUCER = "agentpedia-verify-checks"
HARNESS_VERSION = "1"
STDOUT_LIMIT = 4000
PROGRAMS = {"python3", "python"}


def manifest_path(identifier: str) -> Path:
    return CHECKS_DIR / f"{identifier}.json"


def harness_digest() -> str:
    return sha256_file(Path(__file__).resolve())


def scrubbed_env(home: Path) -> dict[str, str]:
    path = os.environ.get("PATH", "/usr/bin:/bin")
    return {
        "PATH": path,
        "LANG": "C.UTF-8",
        "LC_ALL": "C.UTF-8",
        "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONSAFEPATH": "1",
        "HOME": str(home),
        "TMPDIR": str(home),
        "TEMP": str(home),
        "TMP": str(home),
    }


def validate_argv(argv: object, entry: Path) -> list[str]:
    if not isinstance(argv, list) or not argv or not all(isinstance(item, str) and item for item in argv):
        raise ValueError("argv must be a non-empty list of strings")
    program = argv[0]
    if program not in PROGRAMS:
        candidate = (entry / program).resolve()
        try:
            candidate.relative_to(entry.resolve())
        except ValueError as exc:
            raise ValueError("the program must be python3 or a file inside the entry") from exc
        if not candidate.is_file():
            raise ValueError(f"program not found inside the entry: {program}")
    for arg in argv[1:]:
        if "\x00" in arg or "\n" in arg:
            raise ValueError("an argument contains a newline or NUL")
        if arg.startswith("-"):
            continue
        path = Path(arg)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"argument escapes the entry: {arg}")
    return argv


def clip(text: str) -> tuple[str, bool]:
    if len(text) <= STDOUT_LIMIT:
        return text, False
    return text[:STDOUT_LIMIT] + "\n…[truncated]\n", True


def install_probe(entry: Path, kind: str, root: Path, check_id: str) -> dict:
    expect = "SKILL.md" if kind == "skill" else "AGENT.md"
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="agentpedia-install-") as tmp:
        dest = Path(tmp) / "entry"
        shutil.copytree(entry, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        files = [path for path in dest.rglob("*") if path.is_file()]
        manifest = dest / expect
        present = manifest.is_file() and manifest.stat().st_size > 0
        stdout = (
            f"files={len(files)}\n"
            f"{expect}={'present' if present else 'missing'}\n"
            f"bytes={manifest.stat().st_size if manifest.is_file() else 0}\n"
        )
    duration = int((time.monotonic() - started) * 1000)
    return {
        "id": check_id,
        "kind": "install",
        "argv": ["agentpedia-install-probe", "copy-tree", expect],
        "cwd": entry.relative_to(root).as_posix(),
        "exitCode": 0 if present else 1,
        "expectExit": 0,
        "durationMs": duration,
        "stdout": stdout,
        "stderr": "",
        "ok": present,
        "truncated": False,
    }


def run_eval(entry: Path, spec: dict, root: Path, timeout: int) -> dict:
    argv = validate_argv(spec.get("argv"), entry)
    expect_exit = int(spec.get("expectExit", 0))
    needles = spec.get("expectStdoutContains") or []
    if not isinstance(needles, list) or not all(isinstance(item, str) for item in needles):
        raise ValueError(f"{spec.get('id')} expectStdoutContains must be a list of strings")
    home = Path(tempfile.mkdtemp(prefix="agentpedia-home-"))
    started = time.monotonic()
    try:
        completed = subprocess.run(
            argv,
            cwd=entry,
            env=scrubbed_env(home),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            shell=False,
        )
        stdout, out_cut = clip(completed.stdout)
        stderr, err_cut = clip(completed.stderr)
        exit_code = completed.returncode
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        stdout, out_cut = clip(exc.stdout or "")
        stderr, err_cut = clip((exc.stderr or "") + f"\ntimeout after {timeout}s\n")
        exit_code = None
        timed_out = True
    finally:
        shutil.rmtree(home, ignore_errors=True)
    missing = [needle for needle in needles if needle not in stdout]
    ok = (not timed_out) and exit_code == expect_exit and not missing
    return {
        "id": spec["id"],
        "kind": "eval",
        "argv": argv,
        "cwd": entry.relative_to(root).as_posix(),
        "exitCode": exit_code,
        "expectExit": expect_exit,
        "durationMs": int((time.monotonic() - started) * 1000),
        "stdout": stdout,
        "stderr": stderr,
        "ok": ok,
        "truncated": out_cut or err_cut,
        "missingStdout": missing,
    }


def load_manifest(path: Path) -> dict:
    manifest = load_json(path)
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise CertError(f"{path} schema must be {MANIFEST_SCHEMA}")
    if not manifest.get("id"):
        raise CertError(f"{path} is missing id")
    install = manifest.get("install")
    evals = manifest.get("evals")
    if not isinstance(install, dict) or install.get("kind") != "copy-tree":
        raise CertError(f"{manifest['id']} needs an install probe of kind copy-tree")
    if not isinstance(evals, list) or not evals:
        raise CertError(f"{manifest['id']} needs at least one eval")
    entry = manifest.get("entry")
    if not isinstance(entry, str) or not entry or entry.startswith("/") or ".." in Path(entry).parts:
        raise CertError(f"{manifest['id']} entry must be a relative path inside the repo")
    return manifest


def run_manifest(root: Path, manifest: dict) -> dict:
    identifier = manifest["id"]
    entry = (root / manifest["entry"]).resolve()
    try:
        entry.relative_to(root.resolve())
    except ValueError as exc:
        raise CertError(f"{identifier} entry escapes the repository") from exc
    if not entry.is_dir():
        raise CertError(f"{identifier} entry does not exist: {manifest['entry']}")
    kind = "agent" if identifier.startswith("agent-") else "skill"
    expected_name = identifier.split("-", 1)[1]
    if entry.name != expected_name:
        raise CertError(f"{identifier} entry folder must be named {expected_name}")
    timeout = int(manifest.get("timeoutSec") or 20)
    timeout = max(1, min(timeout, 60))
    install_id = str(manifest["install"].get("id") or "install-copy")
    checks = [install_probe(entry, kind, root, install_id)]
    for spec in manifest["evals"]:
        if not isinstance(spec, dict) or not spec.get("id"):
            raise CertError(f"{identifier} has an eval without an id")
        checks.append(run_eval(entry, spec, root, timeout))
    digest = content_digest(entry)
    commit = git_commit(root, entry)
    if not commit:
        raise CertError(f"{identifier} entry has no git commit. Commit it before recording a run.")
    return {
        "schema": RESULT_SCHEMA,
        "id": identifier,
        "producer": PRODUCER,
        "harnessVersion": HARNESS_VERSION,
        "harnessDigest": harness_digest(),
        "manifestDigest": "",
        "ranAt": datetime.now(timezone.utc).isoformat(),
        "sourceCommit": commit,
        "contentDigest": digest,
        "ok": all(item["ok"] for item in checks),
        "checks": checks,
    }


def execute(root: Path, path: Path) -> dict:
    manifest = load_manifest(path)
    manifest["__path"] = str(path)
    result = run_manifest(root, manifest)
    result["manifestDigest"] = sha256_file(path)
    result.pop("__path", None)
    for check in result["checks"]:
        check.pop("missingStdout", None)
    return result


def write_result(root: Path, result: dict) -> None:
    records = load_records() if root == ROOT else {}
    identifier = result["id"]
    record = records.get(identifier)
    if record is None:
        raise CertError(f"{identifier} has no certificate record. Build the catalog so Listed is issued first.")
    destination = root / "certs" / "results" / f"{identifier}.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if result["ok"]:
        if record["tier"] != "certified":
            record["tier"] = "verified"
        record["contentDigest"] = result["contentDigest"]
        record["sourceCommit"] = result["sourceCommit"]
        save_record(record)
        return
    if record["tier"] == "verified":
        record["tier"] = "listed"
        save_record(record)
        print(f"{identifier}: checks failed. Tier set back to listed.", file=sys.stderr)
    elif record["tier"] == "certified":
        print(
            f"{identifier}: checks failed. Certified was left in place so the build rejects it "
            "until a reviewer withdraws it or the checks pass.",
            file=sys.stderr,
        )


def format_report(result: dict) -> str:
    lines = [
        f"{result['id']}: {'passed' if result['ok'] else 'failed'}",
        f"commit {result['sourceCommit']}",
        f"digest {result['contentDigest']}",
    ]
    for check in result["checks"]:
        lines.append(
            f"- {check['kind']} {check['id']}: exit {check['exitCode']} "
            f"{'ok' if check['ok'] else 'failed'} ({check['durationMs']} ms)"
        )
        if not check["ok"]:
            if check.get("stdout"):
                lines.append("  stdout: " + check["stdout"].strip().replace("\n", "\n  "))
            if check.get("stderr"):
                lines.append("  stderr: " + check["stderr"].strip().replace("\n", "\n  "))
    return "\n".join(lines)


def selected_manifests(identifiers: list[str], run_all: bool) -> list[Path]:
    if run_all or not identifiers:
        return sorted(CHECKS_DIR.glob("*.json"))
    paths = []
    for identifier in identifiers:
        path = manifest_path(identifier)
        if not path.is_file():
            raise CertError(f"no manifest at {path.relative_to(ROOT)}")
        paths.append(path)
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Agentpedia check manifests.")
    parser.add_argument("ids", nargs="*", help="Certificate ids. Default: every manifest.")
    parser.add_argument("--write", action="store_true", help="Write results and update Listed records to Verified when the run passes.")
    args = parser.parse_args(argv)
    try:
        paths = selected_manifests(args.ids, not args.ids)
    except CertError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if not paths:
        print("no check manifests")
        return 0
    failed = False
    for path in paths:
        try:
            result = execute(ROOT, path)
        except (CertError, ValueError) as exc:
            print(f"error: {path.stem}: {exc}", file=sys.stderr)
            failed = True
            continue
        print(format_report(result))
        if args.write:
            try:
                write_result(ROOT, result)
            except CertError as exc:
                print(f"error: {exc}", file=sys.stderr)
                failed = True
                continue
            print(f"wrote certs/results/{result['id']}.json")
        if not result["ok"]:
            failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
