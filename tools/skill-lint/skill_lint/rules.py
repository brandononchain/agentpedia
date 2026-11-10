from __future__ import annotations

import re
from pathlib import Path

from skill_lint.discover import find_skill_file
from skill_lint.frontmatter import Frontmatter, split_frontmatter
from skill_lint.models import Finding, SkillReport

NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MD_LINK_RE = re.compile(r"!?\[([^\]]*)\]\(([^)]+)\)")
BARE_PATH_RE = re.compile(
    r"(?<![\w./-])((?:(?:\./|\.\./)|(?:scripts|references|assets|lib)/)[A-Za-z0-9_./-]+\.[A-Za-z0-9]+)"
)
CODE_FENCE_RE = re.compile(r"^```")
XML_TAG_RE = re.compile(r"</?[A-Za-z!?][^>]*>")
WHEN_RE = re.compile(
    r"\b(use when|use whenever|use if|use in|use during|use for|use after|use before|"
    r"used when|useful when|when the user|when you|when asked|when handling|"
    r"when working|whenever|trigger|invok)",
    re.IGNORECASE,
)
FIRST_PERSON_RE = re.compile(r"\b(i|i'm|i'll|i am|we|we'll|you should|you can|you must)\b", re.IGNORECASE)
EXAMPLE_RE = re.compile(r"\b(example|examples|for example|e\.g\.|sample input|sample output)\b", re.IGNORECASE)
VALIDATION_RE = re.compile(
    r"\b(validate|validation|verify|verification|check(?:list)?|test|assert|confirm|lint)\b",
    re.IGNORECASE,
)
STEP_RE = re.compile(r"(?m)^\s*(?:\d+\.\s|[-*]\s+step\b|#{1,3}\s+step\b)", re.IGNORECASE)
COMMAND_LINE_RE = re.compile(
    r"^\s*(?:\$\s*)?(?:sudo\s+)?(?:npx|npm|pnpm|yarn|pip|pip3|python|python3|uv|cargo|"
    r"curl|wget|git|bash|sh|node|go|docker|kubectl|brew|apt|rg|sed|awk)\b"
)
CURL_PIPE_RE = re.compile(
    r"(curl|wget)\b[^\n|]{0,200}\|\s*(sudo\s+)?(ba)?sh\b",
    re.IGNORECASE,
)
RM_RF_RE = re.compile(r"\brm\s+(?:-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*|-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*)\b")
RM_RF_ROOT_RE = re.compile(r"\brm\s+-[a-zA-Z]*\s+(--\s+)?(/|/\*|~(/|$)|/\$\{?HOME)")
BACKSLASH_PATH_RE = re.compile(r"(?<![\w:])(?:[A-Za-z]:\\|(?:scripts|references|assets|lib)\\|[.]\\|[.][.]\\)[^\s`]+")
ABS_PATH_RE = re.compile(
    r"(?<![\w-])(?:/Users/|/home/|/root/|/etc/|/opt/|/var/|/tmp/|C:\\|D:\\|[A-Za-z]:\\Users\\)[^\s`'\"<>)]+"
)
EXFIL_HOST_RE = re.compile(
    r"https?://[^\s)'\"`]*?(?:webhook\.site|requestbin|pipedream\.net|ngrok(?:-free)?\.(?:io|app)|"
    r"burpcollaborator\.net|interact\.sh|discord(?:app)?\.com/api/webhooks|pastebin\.com|"
    r"hastebin\.com|hookbin\.com)",
    re.IGNORECASE,
)
BEGIN_KEY_RE = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")
AWS_KEY_RE = re.compile(r"\bAKIA[0-9A-Z]{16}\b")
GITHUB_TOKEN_RE = re.compile(r"\b(?:ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b")
OPENAI_KEY_RE = re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")
SLACK_TOKEN_RE = re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")
SECRET_ASSIGN_RE = re.compile(
    r"(?i)\b(api[_-]?key|secret[_-]?key|access[_-]?token|auth[_-]?token|password|passwd|bearer)"
    r"\s*[:=]\s*['\"]?([^\s'\"#]{10,})"
)
PLACEHOLDER_RE = re.compile(
    r"(?i)^(your[_-]?|my[_-]?|example|placeholder|changeme|redacted|todo|xxx+|yyy+|\*{3,}|"
    r"<[^>]+>|\$\{?[A-Z0-9_]+\}?|process\.env)"
)
UNCLEAR_NAMES = {
    "skill",
    "skills",
    "helper",
    "helpers",
    "tmp",
    "temp",
    "misc",
    "test",
    "foo",
    "bar",
    "baz",
    "util",
    "utils",
    "default",
    "general",
    "stuff",
    "dig",
    "new",
    "untitled",
    "demo",
    "sample",
}
SKIP_LINK_PREFIXES = ("http://", "https://", "mailto:", "tel:", "#", "data:")
WORD_RE = re.compile(r"\S+")

MAX_NAME_LEN = 64
MAX_DESCRIPTION_LEN = 1024
MAX_COMPAT_LEN = 500
MAX_BODY_LINES = 500
MAX_BODY_WORDS = 5000
HUGE_FENCE_LINES = 80
MIN_DESCRIPTION_CHARS = 40


def lint_skill(skill_file: Path) -> SkillReport:
    skill_file = skill_file.resolve()
    report = SkillReport(path=str(skill_file), name=None)
    if skill_file.name != "SKILL.md":
        report.findings.append(
            Finding(
                rule_id="spec.filename.case",
                severity="error",
                message=f"skill file must be named SKILL.md (found {skill_file.name})",
                hint="Rename the file to SKILL.md. On Linux the filename is case-sensitive.",
                path=str(skill_file),
            )
        )
    try:
        text = skill_file.read_text(encoding="utf-8")
    except OSError as exc:
        report.findings.append(
            Finding(
                rule_id="scan.file.unreadable",
                severity="error",
                message=f"could not read file: {exc}",
                hint="Check permissions and that the path is a UTF-8 text file.",
                path=str(skill_file),
            )
        )
        return report

    fm = split_frontmatter(text)
    name = _as_str(fm.fields.get("name")) if fm.fields else None
    report.name = name or None
    report.findings.extend(_spec_findings(skill_file, fm, name))
    if fm.parse_error or not fm.present:
        # Still run security scans on the raw file; skip smell rules that need a parsed body.
        report.findings.extend(_security_findings(skill_file, text, 1))
        report.findings.extend(_link_findings(skill_file, text, 1, fm))
        report.findings = _dedupe(report.findings)
        return report

    body = fm.body
    body_start = fm.body_start_line
    description = _as_str(fm.fields.get("description"))
    report.findings.extend(_description_findings(skill_file, fm, description))
    report.findings.extend(_body_findings(skill_file, body, body_start))
    report.findings.extend(_link_findings(skill_file, body, body_start, fm))
    report.findings.extend(_security_findings(skill_file, text, 1))
    report.findings = _dedupe(report.findings)
    return report


def _as_str(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return str(value)


def _spec_findings(skill_file: Path, fm: Frontmatter, name: str | None) -> list[Finding]:
    findings: list[Finding] = []
    path = str(skill_file)
    if not fm.present:
        findings.append(
            Finding(
                rule_id="spec.frontmatter.missing",
                severity="error",
                message="SKILL.md is missing YAML frontmatter delimited by ---",
                hint="Start the file with --- / name and description fields / --- before the Markdown body.",
                path=path,
                line=1,
            )
        )
        return findings
    if fm.parse_error:
        findings.append(
            Finding(
                rule_id="spec.frontmatter.invalid",
                severity="error",
                message=fm.parse_error,
                hint="Use simple YAML keys (name, description, optional license, compatibility, metadata).",
                path=path,
                line=1,
            )
        )
        return findings

    name_line = fm.key_lines.get("name", 2)
    if "name" not in fm.fields:
        findings.append(
            Finding(
                rule_id="spec.name.missing",
                severity="error",
                message="required frontmatter field 'name' is missing",
                hint="Add name: lowercase-hyphen-id matching the parent folder (max 64 characters).",
                path=path,
                line=1,
            )
        )
    else:
        if not name:
            findings.append(
                Finding(
                    rule_id="spec.name.missing",
                    severity="error",
                    message="required frontmatter field 'name' is empty",
                    hint="Set name to a 1-64 character lowercase id such as pdf-processing.",
                    path=path,
                    line=name_line,
                )
            )
        else:
            if len(name) > MAX_NAME_LEN:
                findings.append(
                    Finding(
                        rule_id="spec.name.too-long",
                        severity="error",
                        message=f"name is {len(name)} characters (max {MAX_NAME_LEN})",
                        hint="Shorten the name; it must stay under 64 characters and match the folder name.",
                        path=path,
                        line=name_line,
                    )
                )
            if not NAME_RE.fullmatch(name):
                findings.append(
                    Finding(
                        rule_id="spec.name.invalid",
                        severity="error",
                        message=(
                            "name must be lowercase letters, numbers, and single hyphens "
                            "(no leading, trailing, or consecutive hyphens)"
                        ),
                        hint="Rename to something like invoice-parser; the folder name must match exactly.",
                        path=path,
                        line=name_line,
                    )
                )
            parent = skill_file.parent.name
            # Only check directory match when this looks like a skill folder, not a random filename.
            if parent and parent not in {".", ""} and find_skill_file(skill_file.parent):
                if name and parent != name:
                    findings.append(
                        Finding(
                            rule_id="spec.name.directory-mismatch",
                            severity="error",
                            message=f"name '{name}' does not match parent directory '{parent}'",
                            hint=f"Rename the folder to {name}/ or change name to {parent}.",
                            path=path,
                            line=name_line,
                        )
                    )
            if name.lower() in UNCLEAR_NAMES or (name and len(name) < 3):
                findings.append(
                    Finding(
                        rule_id="smell.name.unclear",
                        severity="warn",
                        message=f"name '{name}' does not describe what the skill does",
                        hint="Use an action-oriented name such as pdf-extract or grokchan-member.",
                        path=path,
                        line=name_line,
                    )
                )

    desc_line = fm.key_lines.get("description", 2)
    if "description" not in fm.fields:
        findings.append(
            Finding(
                rule_id="spec.description.missing",
                severity="error",
                message="required frontmatter field 'description' is missing",
                hint="Add a 1-1024 character description covering what the skill does and when to use it.",
                path=path,
                line=1,
            )
        )
    else:
        description = _as_str(fm.fields.get("description")).strip()
        if not description:
            findings.append(
                Finding(
                    rule_id="spec.description.missing",
                    severity="error",
                    message="required frontmatter field 'description' is empty",
                    hint="Write what the skill does, when to trigger it, and a few matching keywords.",
                    path=path,
                    line=desc_line,
                )
            )
        elif len(description) > MAX_DESCRIPTION_LEN:
            findings.append(
                Finding(
                    rule_id="spec.description.too-long",
                    severity="error",
                    message=f"description is {len(description)} characters (max {MAX_DESCRIPTION_LEN})",
                    hint="Trim the description and move extra detail into the Markdown body or references/.",
                    path=path,
                    line=desc_line,
                )
            )

    compat = fm.fields.get("compatibility")
    if compat is not None:
        compat_text = _as_str(compat)
        if compat_text and len(compat_text) > MAX_COMPAT_LEN:
            findings.append(
                Finding(
                    rule_id="spec.compatibility.too-long",
                    severity="error",
                    message=f"compatibility is {len(compat_text)} characters (max {MAX_COMPAT_LEN})",
                    hint="Keep compatibility to a short environment note (intended product, packages, network).",
                    path=path,
                    line=fm.key_lines.get("compatibility", 1),
                )
            )
    return findings


def _description_findings(skill_file: Path, fm: Frontmatter, description: str) -> list[Finding]:
    findings: list[Finding] = []
    description = description.strip()
    if not description or len(description) > MAX_DESCRIPTION_LEN:
        return findings
    path = str(skill_file)
    line = fm.key_lines.get("description", 2)
    if XML_TAG_RE.search(description):
        findings.append(
            Finding(
                rule_id="smell.description.xml",
                severity="error",
                message="description contains XML/HTML tags, which can inject unexpected instructions",
                hint="Remove tags from the description; keep it plain text so hosts cannot treat markup as prompts.",
                path=path,
                line=line,
            )
        )
    if not WHEN_RE.search(description):
        findings.append(
            Finding(
                rule_id="smell.description.no-when",
                severity="warn",
                message="description does not say when the skill should be used",
                hint="Add a clause like 'Use when the user asks to extract or merge PDFs.' so hosts can match it.",
                path=path,
                line=line,
            )
        )
    if len(description) < MIN_DESCRIPTION_CHARS:
        findings.append(
            Finding(
                rule_id="smell.description.vague",
                severity="warn",
                message=f"description is only {len(description)} characters and is likely too vague to match well",
                hint="Write what the skill does, when to use it, and trigger keywords (aim for a full sentence or two).",
                path=path,
                line=line,
            )
        )
    # Imperative "Use when..." is accepted trigger language, so ignore a leading Use.
    check = description
    if re.match(r"^use\b", check, re.IGNORECASE):
        check = check[3:]
    if FIRST_PERSON_RE.search(check):
        findings.append(
            Finding(
                rule_id="smell.description.not-third-person",
                severity="info",
                message="description is not written in third person",
                hint="Prefer 'Extracts PDF text and merges files. Use when handling PDFs.' over I/you phrasing.",
                path=path,
                line=line,
            )
        )
    return findings


def _body_findings(skill_file: Path, body: str, body_start: int) -> list[Finding]:
    findings: list[Finding] = []
    path = str(skill_file)
    body_lines = body.splitlines()
    words = WORD_RE.findall(body)
    if len(body_lines) > MAX_BODY_LINES:
        findings.append(
            Finding(
                rule_id="smell.body.too-long-lines",
                severity="warn",
                message=f"body is {len(body_lines)} lines (recommended maximum {MAX_BODY_LINES})",
                hint="Move reference material, long examples, and schemas into references/ and link them from SKILL.md.",
                path=path,
                line=body_start,
            )
        )
    if len(words) > MAX_BODY_WORDS:
        findings.append(
            Finding(
                rule_id="smell.body.too-long-words",
                severity="warn",
                message=f"body is {len(words)} words (recommended maximum {MAX_BODY_WORDS})",
                hint="Delegate details to references/ or scripts/ so progressive disclosure can skip unused text.",
                path=path,
                line=body_start,
            )
        )

    fence_start = None
    fence_start_line = 0
    for idx, line in enumerate(body_lines):
        if line.startswith("```"):
            if fence_start is None:
                fence_start = idx
                fence_start_line = body_start + idx
            else:
                fence_len = idx - fence_start - 1
                if fence_len >= HUGE_FENCE_LINES:
                    findings.append(
                        Finding(
                            rule_id="smell.body.huge-inline-blob",
                            severity="warn",
                            message=f"fenced block is {fence_len} lines (threshold {HUGE_FENCE_LINES})",
                            hint="Move large templates or scripts into references/ or scripts/ and link to them.",
                            path=path,
                            line=fence_start_line,
                        )
                    )
                fence_start = None
    if not EXAMPLE_RE.search(body):
        findings.append(
            Finding(
                rule_id="smell.example.missing",
                severity="warn",
                message="body has no example of inputs, outputs, or usage",
                hint="Add an Example section with one realistic request and the expected action or output.",
                path=path,
                line=body_start,
            )
        )
    if len(words) >= 150 and not STEP_RE.search(body):
        findings.append(
            Finding(
                rule_id="smell.workflow.stepless",
                severity="warn",
                message="longer body has no numbered steps or Step headings",
                hint="Break the workflow into numbered steps the agent can follow and verify.",
                path=path,
                line=body_start,
            )
        )
    if len(words) >= 80 and not VALIDATION_RE.search(body):
        findings.append(
            Finding(
                rule_id="smell.validation.missing",
                severity="info",
                message="body never mentions validation, verification, tests, or checks",
                hint="Tell the agent how to check its work (run tests, compare counts, or ask the user to confirm).",
                path=path,
                line=body_start,
            )
        )

    command_lines = [line for line in body_lines if COMMAND_LINE_RE.search(_strip_fence_prompt(line))]
    scripts_dir = skill_file.parent / "scripts"
    has_scripts = scripts_dir.is_dir() and any(scripts_dir.iterdir())
    if len(command_lines) >= 6 and not has_scripts:
        findings.append(
            Finding(
                rule_id="smell.scripts.missing",
                severity="info",
                message=f"body lists {len(command_lines)} shell-like commands but there is no scripts/ directory",
                hint="Bundle repeated commands as scripts/ helpers so the agent runs deterministic code instead of improvising.",
                path=path,
                line=body_start,
            )
        )

    references_dir = skill_file.parent / "references"
    has_refs = references_dir.is_dir() and any(references_dir.iterdir())
    local_md_links = any(
        _is_relative_target(target) and target.split("?", 1)[0].split("#", 1)[0].endswith(".md")
        for target in _markdown_targets(body)
    )
    if (len(body_lines) > 400 or len(words) > 2500) and not has_refs and not local_md_links:
        findings.append(
            Finding(
                rule_id="smell.detail.undelegated",
                severity="warn",
                message="long skill body does not delegate detail to references/ or linked Markdown files",
                hint="Keep SKILL.md as the entrypoint and move deep docs into references/ loaded only when needed.",
                path=path,
                line=body_start,
            )
        )
    return findings


def _strip_fence_prompt(line: str) -> str:
    return re.sub(r"^\s*[-*]\s+", "", line)


def _markdown_targets(text: str) -> list[str]:
    return [match.group(2).strip() for match in MD_LINK_RE.finditer(text)]


def _is_relative_target(target: str) -> bool:
    cleaned = target.strip().strip("<>").strip()
    if not cleaned:
        return False
    lower = cleaned.lower()
    if lower.startswith(SKIP_LINK_PREFIXES):
        return False
    return True


def _link_findings(skill_file: Path, body: str, body_start: int, fm: Frontmatter) -> list[Finding]:
    findings: list[Finding] = []
    path = str(skill_file)
    root = skill_file.parent
    seen: set[tuple[str, int | None]] = set()

    def add(rule_id: str, severity: str, message: str, hint: str, line: int | None) -> None:
        key = (rule_id, message, line)
        if key in seen:
            return
        seen.add(key)
        findings.append(
            Finding(rule_id=rule_id, severity=severity, message=message, hint=hint, path=path, line=line)
        )

    body_lines = body.splitlines()
    for idx, line in enumerate(body_lines):
        line_no = body_start + idx
        if BACKSLASH_PATH_RE.search(line):
            add(
                "link.path.backslash",
                "warn",
                "path uses backslashes; agents resolve skill files as a POSIX tree",
                "Write relative paths with forward slashes, such as scripts/extract.py.",
                line_no,
            )
        for match in MD_LINK_RE.finditer(line):
            target = match.group(2).strip().strip("<>").split()[0] if match.group(2).strip() else ""
            _check_relative_target(root, target, line_no, add)
        for match in BARE_PATH_RE.finditer(line):
            _check_relative_target(root, match.group(1), line_no, add)

    # Also scan frontmatter for relative refs (rare).
    if fm.raw:
        for match in MD_LINK_RE.finditer(fm.raw):
            _check_relative_target(root, match.group(2).strip(), fm.key_lines.get("description"), add)
    return findings


def _check_relative_target(root: Path, target: str, line: int | None, add) -> None:
    cleaned = target.strip().strip("<>").strip()
    if not cleaned or not _is_relative_target(cleaned):
        return
    resource = cleaned.split()[0]
    resource = resource.split("#", 1)[0].split("?", 1)[0]
    if not resource or resource.endswith("/"):
        return
    # Ignore bare words without a slash or extension-looking path already handled.
    candidate = (root / resource).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        # Path escapes the skill folder with too many .. — still check existence
        pass
    if not candidate.exists():
        add(
            "link.relative.missing",
            "error",
            f"relative path does not exist: {resource}",
            "Create the file under the skill folder or update the link to a real references/ or scripts/ path.",
            line,
        )


def _security_findings(skill_file: Path, text: str, start_line: int) -> list[Finding]:
    findings: list[Finding] = []
    path = str(skill_file)
    lines = text.splitlines()
    for idx, line in enumerate(lines):
        line_no = start_line + idx
        if BEGIN_KEY_RE.search(line) or AWS_KEY_RE.search(line) or GITHUB_TOKEN_RE.search(line) or OPENAI_KEY_RE.search(line) or SLACK_TOKEN_RE.search(line):
            findings.append(
                Finding(
                    rule_id="security.secret",
                    severity="error",
                    message="possible hardcoded credential or private key",
                    hint="Remove the secret and tell the agent to read it from an env var or a secret store.",
                    path=path,
                    line=line_no,
                )
            )
        for assign in SECRET_ASSIGN_RE.finditer(line):
            value = assign.group(2)
            if PLACEHOLDER_RE.search(value):
                continue
            if value.startswith("http://") or value.startswith("https://"):
                continue
            findings.append(
                Finding(
                    rule_id="security.secret",
                    severity="error",
                    message=f"possible hardcoded secret assignment for '{assign.group(1)}'",
                    hint="Replace the literal value with an environment variable or a user-provided secret.",
                    path=path,
                    line=line_no,
                )
            )
        if CURL_PIPE_RE.search(line):
            findings.append(
                Finding(
                    rule_id="security.curl-pipe-sh",
                    severity="error",
                    message="risky piped install: download piped directly into a shell",
                    hint="Download, inspect, and run scripts as separate steps; never curl | sh from a skill.",
                    path=path,
                    line=line_no,
                )
            )
        if RM_RF_RE.search(line):
            severity = "error" if RM_RF_ROOT_RE.search(line) else "warn"
            findings.append(
                Finding(
                    rule_id="security.rm-rf",
                    severity=severity,
                    message="skill includes rm -rf, which agents can execute against the wrong path",
                    hint="Delete specific files, confine cleanup to a temp directory, and avoid recursive force-deletes.",
                    path=path,
                    line=line_no,
                )
            )
        for match in EXFIL_HOST_RE.finditer(line):
            findings.append(
                Finding(
                    rule_id="security.exfil-url",
                    severity="warn",
                    message=f"URL looks like a data-exfil or webhook sink: {match.group(0)}",
                    hint="Remove unexpected webhook, tunnel, or pastebin endpoints from skill instructions and scripts.",
                    path=path,
                    line=line_no,
                )
            )
        for match in ABS_PATH_RE.finditer(line):
            findings.append(
                Finding(
                    rule_id="security.absolute-path",
                    severity="warn",
                    message=f"hardcoded absolute path: {match.group(0)}",
                    hint="Use paths relative to the skill folder (scripts/..., references/...) so the skill is portable.",
                    path=path,
                    line=line_no,
                )
            )
    return findings


def _dedupe(findings: list[Finding]) -> list[Finding]:
    seen: set[tuple] = set()
    out: list[Finding] = []
    for finding in findings:
        key = (finding.rule_id, finding.message, finding.line, finding.path)
        if key in seen:
            continue
        seen.add(key)
        out.append(finding)
    return out
