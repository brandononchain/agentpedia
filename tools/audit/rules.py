"""Rule families S (text), C (code), and D (dependencies).

Each finding carries a stable id, a severity, a CWE, an OWASP mapping, the
file and line, an escaped evidence snippet, and a remediation.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from audit.models import Finding, Rule, show_evidence
from audit.popular import POPULAR

RULES: list[Rule] = [
    Rule("S01", "Skill and agent text", "high or critical", "Hidden, bidi, zero-width, or Unicode tag characters.", "Remove the invisible characters. Write the instruction in ordinary text.", "CWE-176", ("ASI01", "LLM01")),
    Rule("S02", "Skill and agent text", "critical", "Instruction-override phrases such as \"ignore previous instructions\".", "Describe the attack without embedding the override. Tell the agent to treat untrusted text as data.", "CWE-94", ("ASI01", "LLM01")),
    Rule("S03", "Skill and agent text", "high", "Secrecy phrases that tell the agent to hide a step from the user.", "Say what the agent should show the user. Do not instruct it to conceal its actions.", "CWE-200", ("ASI09", "LLM07")),
    Rule("S04", "Skill and agent text", "high", "A request that the user paste a credential, token, or secret file.", "Tell the user to set a secret in the environment themselves. Do not ask them to paste it.", "CWE-522", ("ASI03", "LLM02")),
    Rule("S05", "Skill and agent text", "medium", "A long base64 or hex blob that can hide a payload.", "Remove the blob. If it is a sample, describe it instead of embedding it.", "CWE-506", ("ASI01", "LLM01")),
    Rule("S06", "Skill and agent text", "critical", "An instruction to write global agent config or a shell startup file.", "Print a draft in the reply. Do not tell the agent to write CLAUDE.md, AGENTS.md, or files under the home directory.", "CWE-506", ("ASI05", "LLM06")),
    Rule("S07", "Skill and agent text", "medium", "A description broad enough to hijack when the skill triggers.", "Say the specific job and when to use the skill. Do not claim every request.", "CWE-441", ("ASI02", "LLM01")),
    Rule("S08", "Skill and agent text", "high", "A send, delete, pay, or push without a confirm step nearby.", "Require the user to confirm that action in the same steps, or tell the agent not to do it.", "CWE-862", ("ASI02", "LLM06")),
    Rule("S09", "Skill and agent text", "high", "Fetch a remote document and follow what it says.", "Fetch is data. Do not tell the agent to execute or follow instructions from a URL.", "CWE-829", ("ASI04", "LLM01")),
    Rule("S10", "Skill and agent text", "medium or high", "HTML comments or a long run of blank lines that can hide instructions.", "Delete the comment or the padding. Put every instruction where a reviewer can see it.", "CWE-506", ("ASI01", "LLM01")),
    Rule("C01", "Bundled code", "critical", "An opaque binary, or a minified blob, shipped inside the entry.", "Ship source a reviewer can read. Do not include executables or minified payloads.", "CWE-506", ("ASI05", "LLM03")),
    Rule("C02", "Bundled code", "high", "eval, exec, os.system, or a subprocess started with a shell.", "Call a fixed argument list with shell left off. Do not evaluate a string.", "CWE-78", ("ASI05", "LLM05")),
    Rule("C03", "Bundled code", "medium", "A network call from bundled code.", "Keep the script local. If a later phase allows a host, name it and do not follow what it returns.", "CWE-829", ("ASI04", "LLM06")),
    Rule("C04", "Bundled code", "high", "A read of a secret file, a keychain, or the process environment.", "Take only the inputs the user passed on the command line. Do not open ~/.ssh, .env, or ~/.aws.", "CWE-522", ("ASI03", "LLM02")),
    Rule("C05", "Bundled code", "high", "A write to an absolute path or a path that leaves the work directory.", "Write only paths the user passed, and reject paths that escape the working directory.", "CWE-22", ("ASI05", "LLM06")),
    Rule("C06", "Bundled code", "critical", "Persistence via cron, launchd, systemd, or a shell startup file.", "Do not install a scheduled task or edit a startup file.", "CWE-506", ("ASI05", "LLM06")),
    Rule("C07", "Bundled code", "high", "Obfuscation such as base64 decode, hex decode, or a chain of chr calls.", "Write the operation in source a reviewer can read.", "CWE-506", ("ASI05", "LLM01")),
    Rule("C08", "Bundled code", "critical", "A download piped into a shell.", "Do not pipe curl or wget into sh. Vendor the script and review it.", "CWE-829", ("ASI04", "LLM03")),
    Rule("D01", "Dependencies", "medium", "A dependency that is not pinned to an exact version.", "Pin the version with == or an exact package.json version, and commit a lock.", "CWE-829", ("ASI04", "LLM03")),
    Rule("D02", "Dependencies", "high", "An import of a third-party package that the entry does not declare.", "Declare the package in requirements.txt or package.json, pinned.", "CWE-829", ("ASI04", "LLM03")),
    Rule("D03", "Dependencies", "high", "An instruction or script that installs packages at runtime.", "Declare dependencies in the entry. Do not run pip install or npm install from the skill.", "CWE-829", ("ASI04", "LLM03")),
    Rule("D04", "Dependencies", "high", "A package name one edit away from a popular package.", "Use the real package name. A one-character lookalike is a typosquat.", "CWE-829", ("ASI04", "LLM03")),
    Rule("D05", "Dependencies", "info", "A dependency manifest with no lock or hash.", "Add a lockfile, or pin each requirement with --hash.", "CWE-829", ("ASI04", "LLM03")),
]

_BY_ID = {rule.id: rule for rule in RULES}

_BIDI = set(range(0x202A, 0x202F)) | set(range(0x2066, 0x206A))
_ZERO = {0x200B, 0x200C, 0x200D, 0x2060, 0xFEFF, 0x180E}
_TAG_START, _TAG_END = 0xE0000, 0xE007F

_OVERRIDE = re.compile(
    r"(?i)\b("
    r"ignore (?:all |any )?(?:previous|prior|above|earlier) (?:instructions|prompts|rules|directions|context)"
    r"|disregard (?:all |any )?(?:previous|prior|above|earlier)"
    r"|forget (?:all |everything |any )?(?:previous|prior|above)"
    r"|do not follow (?:the )?(?:previous|prior|original|system)"
    r"|override (?:the |your )?(?:system|developer) (?:prompt|message|instructions)"
    r"|new (?:system |developer )?instructions\b"
    r"|you are now (?:a |an |the )"
    r")"
)
_SECRECY = re.compile(
    r"(?i)\b("
    r"(?:do not|don't|dont|never) (?:tell|inform|show|mention) (?:the )?(?:user|human)(?!\s+to\b)"
    r"|hide (?:this|these|it) from (?:the )?user"
    r"|keep (?:this|these) (?:secret|hidden) from"
    r"|without (?:telling|informing) the user"
    r")"
)
_CREDENTIAL = re.compile(
    r"(?i)\b(?:paste|share|send me|provide|enter|give me) (?:your|the|a|an) (?:api[_ ]?key|access[_ ]?token|password|secret|credential)s?\b"
    r"|\bask (?:the user )?for (?:your |the |a |an )?(?:api[_ ]?key|access[_ ]?token|password|secret|credential)s?\b"
    r"|\b(?:read|cat|open|print)\b.{0,40}(?:~/\.ssh|\.env\b|~/\.aws|keychain)"
)
_B64 = re.compile(r"\b[A-Za-z0-9+/]{80,}={0,2}\b")
_HEX = re.compile(r"\b[0-9a-fA-F]{80,}\b")
_CONFIG_PATH = re.compile(
    r"(?i)(?<![A-Za-z0-9:/])(?:~/\.(?:claude|cursor|codex|agents)|~/\.(?:bashrc|zshrc|bash_profile|profile)|(?:CLAUDE|AGENTS)\.md\b|\.claude/|\.cursor/)"
)
_WRITE = re.compile(r"(?i)\b(?:write|writes|append|save|create|overwrite|update|edit|modify|install|copy|refresh|draft|drafts)\b")
_OVERBROAD = re.compile(
    r"(?i)\b(?:"
    r"always use this"
    r"|for (?:every|any|all) (?:request|task|prompt|message|query)"
    r"|regardless of"
    r"|ignore other skills"
    r"|prefer this (?:skill|tool) over"
    r"|use this (?:skill|tool) for (?:everything|anything)"
    r")"
)
_CONSEQUENTIAL = re.compile(
    r"(?i)\b(?:"
    r"git push\b|force-push|force push"
    r"|delete (?:the |a )?(?:file|repo|repository|branch|database|account|record)s?"
    r"|\brm\s+-[a-zA-Z]*r"
    r"|(?:pay|wire|transfer)\b.{0,24}\b(?:money|funds|usd|invoice|wallet)"
    r"|(?:send|post)\b.{0,32}\b(?:email|e-mail|message|slack|webhook|inbox|payment)"
    r")"
)
_CONFIRM = re.compile(r"(?i)\b(?:confirm|confirmation|approval|approve|ask the user|user confirms|only if the user|wait for the user)\b")
_FETCH_FOLLOW = re.compile(
    r"(?i)\b(?:curl|wget|fetch|download)\b.{0,100}\b(?:and (?:then )?(?:run|execute|follow|obey)|follow (?:the )?instructions|do what it says)\b"
    r"|\b(?:follow|obey|execute)\b.{0,40}\b(?:the )?(?:instructions|steps) (?:at|from)\s+https?://"
)
_HTML_COMMENT = re.compile(r"<!--(.*?)-->", re.DOTALL)
_EVAL = re.compile(r"(?i)\b(?:eval|exec)\s*\(|\bos\.system\s*\(|\bshell\s*=\s*True\b|\bsubprocess\.(?:Popen|run|call|check_output|check_call)\s*\([^)]*\bshell\s*=\s*True")
_NETWORK = re.compile(
    r"(?i)(?<![A-Za-z0-9_-])(?:import\s+requests|from\s+requests\b|requests\.[A-Za-z_]|import\s+httpx|httpx\.[A-Za-z_]|import\s+aiohttp|aiohttp\.[A-Za-z_]|urllib\.request|http\.client)\b"
    r"|\bsocket\.(?:socket|connect|create_connection)\s*\("
    r"|(?<![A-Za-z0-9_])(?:curl|wget)\b"
    r"|\bfetch\s*\(|\bXMLHttpRequest\b|\bnet\.Dial\b"
)
_SECRET_READ = re.compile(
    r"(?i)~/\.ssh|~/\.aws|~/\.gnupg|\bid_rsa\b|keychain|credentials\.json|(?:^|[^A-Za-z0-9_])\.env\b|\bos\.environ\b|\bos\.getenv\s*\(|\bprocess\.env\b"
)
_OUTSIDE = re.compile(r"""(?i)open\(\s*['\"](?:/|~)|Path\(\s*['\"](?:/|~)|Path\.home\s*\(|\.\./\.\.""")
_PERSIST = re.compile(r"(?i)\bcrontab\b|\blaunchctl\b|LaunchAgents|\bsystemd\b|~/\.bashrc|~/\.zshrc")
_OBFUSC = re.compile(r"(?i)base64\.b64decode|codecs\.decode|bytes\.fromhex|binascii\.(?:a2b_base64|unhexlify)|(?:\\x[0-9a-fA-F]{2}){8,}|(?:\bchr\(\d+\)\s*\+){4,}")
_CURL_PIPE = re.compile(r"(?i)\b(?:curl|wget)\b[^\n|]{0,200}\|\s*(?:sudo\s+)?(?:ba)?sh\b")
_RUNTIME_INSTALL = re.compile(r"(?i)\b(?:pip3?|npm|pnpm|yarn|bun)\s+install\b|\bnpx\s+[A-Za-z@]|\byarn\s+add\b|\bpnpm\s+add\b")
_NEG = re.compile(r"(?i)\b(?:do not|does not|don't|dont|never|avoid|without|will not|won't)\b")
_IMPORT = re.compile(r"(?m)^(?:import|from)\s+([A-Za-z_][\w.]*)")
_REQ_LINE = re.compile(r"^\s*([A-Za-z0-9_.\-]+)")
_IMAGE_MAGIC = (b"\x89PNG", b"\xff\xd8\xff", b"GIF8", b"RIFF")
_EXEC_EXT = {".exe", ".dll", ".so", ".dylib", ".bin", ".wasm", ".pyc", ".class", ".com", ".scr"}
_CODE_EXT = {".py", ".sh", ".bash", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".rb", ".go", ".rs", ".php", ".pl", ".ps1"}
_TEXT_EXT = _CODE_EXT | {".md", ".txt", ".rst", ".yml", ".yaml", ".json", ".toml", ".ini", ".cfg", ".csv"}


def rule_catalog() -> list[dict]:
    return [rule.to_dict() for rule in RULES]


def _finding(rule_id: str, severity: str, path: str, line: int, evidence: str, message: str) -> Finding:
    rule = _BY_ID[rule_id]
    return Finding(
        rule_id=rule_id,
        severity=severity,
        path=path,
        line=line,
        evidence=show_evidence(evidence),
        message=message,
        remediation=rule.remediation,
        cwe=rule.cwe,
        owasp=rule.owasp,
    )


def _negated(line: str, start: int) -> bool:
    return _NEG.search(line[max(0, start - 48) : start]) is not None


def _line_at(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def _description(text: str) -> str:
    if not text.startswith("---"):
        return ""
    lines = text.splitlines()
    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
    if end is None:
        return ""
    collected: list[str] = []
    capturing = False
    for line in lines[1:end]:
        if re.match(r"^description\s*:", line):
            capturing = True
            rest = line.split(":", 1)[1].strip()
            if rest and rest not in {">", ">-", "|", "|-"}:
                collected.append(rest.strip("'\""))
            continue
        if capturing:
            if line.startswith((" ", "\t")):
                collected.append(line.strip())
                continue
            break
    return " ".join(part for part in collected if part)


def scan_text(path: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    lines = text.splitlines()
    seen: set[tuple[str, int]] = set()

    def add(rule_id: str, severity: str, line_no: int, evidence: str, message: str) -> None:
        key = (rule_id, line_no)
        if key in seen:
            return
        seen.add(key)
        findings.append(_finding(rule_id, severity, path, line_no, evidence, message))

    for index, line in enumerate(lines, start=1):
        severity = ""
        for char in line:
            code = ord(char)
            if code in _BIDI or _TAG_START <= code <= _TAG_END:
                severity = "critical"
                break
            if code in _ZERO:
                severity = severity or "high"
        if severity:
            add("S01", severity, index, line, "This line contains a hidden or direction-changing character.")

        for pattern, rule_id, severity, message in (
            (_OVERRIDE, "S02", "critical", "This line tells the agent to discard earlier instructions."),
            (_SECRECY, "S03", "high", "This line tells the agent to hide a step from the user."),
            (_FETCH_FOLLOW, "S09", "high", "This line fetches a remote document and tells the agent to follow it."),
        ):
            match = pattern.search(line)
            if match and not _negated(line, match.start()):
                add(rule_id, severity, index, line, message)

        match = _CREDENTIAL.search(line)
        if match and not _negated(line, match.start()):
            add("S04", "high", index, line, "This line asks for a credential or a secret file.")

        if _B64.search(line) or _HEX.search(line):
            add("S05", "medium", index, line, "This line contains a long encoded blob.")

        for match in _CONFIG_PATH.finditer(line):
            left = max(0, match.start() - 80)
            right = min(len(line), match.end() + 80)
            verb = None
            for candidate in _WRITE.finditer(line[left:right]):
                absolute = left + candidate.start()
                if not _negated(line, absolute):
                    verb = candidate
                    break
            if verb:
                add("S06", "critical", index, line, "This line tells the agent to write agent config or a startup file.")
                break

        match = _CONSEQUENTIAL.search(line)
        if match and not _negated(line, match.start()):
            window = "\n".join(lines[max(0, index - 9) : min(len(lines), index + 8)])
            if not _CONFIRM.search(window):
                add("S08", "high", index, line, "This line takes a consequential action without a confirm step nearby.")

    description = _description(text)
    if description and _OVERBROAD.search(description):
        add("S07", "medium", 1, description, "The description claims a trigger broader than one job.")

    for match in _HTML_COMMENT.finditer(text):
        body = match.group(1).strip()
        if len(body) >= 20:
            add("S10", "medium", _line_at(text, match.start()), match.group(0), "An HTML comment hides text that an agent still reads.")

    blank = 0
    blank_at = 0
    for index, line in enumerate(lines, start=1):
        if line.strip() == "":
            if blank == 0:
                blank_at = index
            blank += 1
        else:
            blank = 0
        if blank == 40:
            add("S10", "high", blank_at, "blank lines", "Forty blank lines can hide instructions below the visible page.")
            break

    for match in _RUNTIME_INSTALL.finditer(text):
        line_no = _line_at(text, match.start())
        line = lines[line_no - 1] if lines else text
        line_start = text.rfind("\n", 0, match.start()) + 1
        if not _negated(line, match.start() - line_start):
            add("D03", "high", line_no, line, "This line installs a package while the skill runs.")

    return findings


def scan_code(path: str, text: str, data: bytes) -> list[Finding]:
    findings: list[Finding] = []
    suffix = Path(path).suffix.lower()
    if suffix in _EXEC_EXT or (b"\0" in data[:8192] and not data.startswith(_IMAGE_MAGIC)):
        findings.append(_finding("C01", "critical", path, 1, path, "This file is an opaque binary."))
        return findings
    if b"\0" in data[:8192] and data.startswith(_IMAGE_MAGIC):
        findings.append(_finding("C01", "info", path, 1, path, "This file is an image. Phase 1 does not inspect pixels."))
        return findings
    lines = text.splitlines()
    if suffix in {".js", ".mjs", ".cjs", ".css"} and any(len(line) > 500 for line in lines):
        findings.append(_finding("C01", "high", path, 1, lines[0][:180] if lines else path, "This file looks minified."))

    checks = (
        (_EVAL, "C02", "high", "This line evaluates a string or starts a shell."),
        (_NETWORK, "C03", "medium", "This line makes a network call."),
        (_SECRET_READ, "C04", "high", "This line reads a secret file or the environment."),
        (_OUTSIDE, "C05", "high", "This line writes outside the working directory."),
        (_PERSIST, "C06", "critical", "This line installs persistence."),
        (_OBFUSC, "C07", "high", "This line is obfuscated."),
        (_CURL_PIPE, "C08", "critical", "This line pipes a download into a shell."),
    )
    seen: set[tuple[str, int]] = set()
    for index, line in enumerate(lines, start=1):
        for pattern, rule_id, severity, message in checks:
            if pattern.search(line) and (rule_id, index) not in seen:
                seen.add((rule_id, index))
                findings.append(_finding(rule_id, severity, path, index, line, message))
    findings.extend(scan_text(path, text))
    return findings


def _damerau(left: str, right: str) -> int:
    if abs(len(left) - len(right)) > 2:
        return 3
    height = len(left) + 1
    width = len(right) + 1
    grid = [[0] * width for _ in range(height)]
    for i in range(height):
        grid[i][0] = i
    for j in range(width):
        grid[0][j] = j
    for i, a in enumerate(left, start=1):
        for j, b in enumerate(right, start=1):
            cost = 0 if a == b else 1
            grid[i][j] = min(grid[i - 1][j] + 1, grid[i][j - 1] + 1, grid[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and left[i - 1] == right[j - 2] and left[i - 2] == right[j - 1]:
                grid[i][j] = min(grid[i][j], grid[i - 2][j - 2] + 1)
    return grid[-1][-1]


def typosquat(name: str) -> str | None:
    lowered = name.lower()
    if lowered in POPULAR or len(lowered) < 4:
        return None
    for popular in POPULAR:
        if abs(len(popular) - len(lowered)) > 1:
            continue
        if _damerau(lowered, popular) == 1:
            return popular
    return None


def _stdlib() -> set[str]:
    names = getattr(sys, "stdlib_module_names", frozenset())
    return set(names) | {"__future__"}


def _declared_python(root: Path) -> tuple[set[str], bool, bool]:
    """Return declared distribution names, whether any manifest exists, and whether it is locked."""
    declared: set[str] = set()
    manifest = False
    locked = False
    requirements = list(root.rglob("requirements*.txt")) + list(root.rglob("requirements*.in"))
    for path in requirements:
        manifest = True
        text = path.read_text(encoding="utf-8", errors="replace")
        if "--hash=" in text or path.name.endswith(".lock"):
            locked = True
        for line in text.splitlines():
            stripped = line.split("#", 1)[0].strip()
            if not stripped or stripped.startswith("-"):
                continue
            match = _REQ_LINE.match(stripped)
            if not match:
                continue
            name = match.group(1)
            declared.add(name.lower())
            if not re.search(r"==[^=]", stripped):
                declared.add("unpinned:" + name.lower())
    if (root / "requirements.lock").is_file() or (root / "poetry.lock").is_file() or (root / "Pipfile.lock").is_file():
        locked = True
    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        manifest = True
        text = pyproject.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"""['\"]([A-Za-z0-9_.\-]+)(?:\[[^\]]+\])?(?:[<>=!~]=?[^'\"]+)?['\"]""", text):
            declared.add(match.group(1).lower())
    return declared, manifest, locked


def _imports(root: Path) -> set[str]:
    found: set[str] = set()
    local = {path.stem for path in root.rglob("*.py")}
    stdlib = _stdlib()
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in _IMPORT.finditer(text):
            top = match.group(1).split(".", 1)[0]
            if top in stdlib or top in local:
                continue
            found.add(top)
    return found


def scan_supply(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not root.is_dir():
        return findings
    declared, manifest, locked = _declared_python(root)
    unpinned = sorted(name.split(":", 1)[1] for name in declared if name.startswith("unpinned:"))
    names = {name for name in declared if not name.startswith("unpinned:")}
    for name in unpinned:
        findings.append(
            _finding("D01", "medium", "requirements.txt", 1, name, f"{name} is not pinned to an exact version.")
        )
    package_json = root / "package.json"
    if package_json.is_file():
        manifest = True
        text = package_json.read_text(encoding="utf-8", errors="replace")
        try:
            import json

            data = json.loads(text)
        except json.JSONDecodeError:
            data = {}
        deps = {}
        if isinstance(data, dict):
            for key in ("dependencies", "devDependencies", "optionalDependencies"):
                block = data.get(key)
                if isinstance(block, dict):
                    deps.update(block)
        for name, version in deps.items():
            names.add(str(name).lower())
            spec = str(version).strip()
            if spec in {"", "*", "latest"} or spec[:1] in "^~><" or "x" in spec.lower():
                findings.append(_finding("D01", "medium", "package.json", 1, f"{name}@{spec}", f"{name} is not pinned."))
        if (root / "package-lock.json").is_file() or (root / "pnpm-lock.yaml").is_file() or (root / "yarn.lock").is_file():
            locked = True
    imports = _imports(root)
    for name in sorted(imports):
        if name.lower() not in names and name.lower().replace("_", "-") not in names:
            findings.append(
                _finding("D02", "high", f"{name}.py", 1, f"import {name}", f"{name} is imported and not declared.")
            )
    for name in sorted(names):
        hit = typosquat(name)
        if hit:
            findings.append(
                _finding("D04", "high", "requirements.txt", 1, name, f"{name} is one edit away from {hit}.")
            )
    if manifest and not locked and names:
        findings.append(
            _finding("D05", "info", "requirements.txt", 1, "no lock", "Dependencies are declared without a lock or a hash.")
        )
    return findings


def scan_bytes(path: str, data: bytes) -> list[Finding]:
    suffix = Path(path).suffix.lower()
    if b"\0" in data[:8192] or suffix in _EXEC_EXT:
        return scan_code(path, "", data)
    if suffix not in _TEXT_EXT and suffix not in _CODE_EXT:
        return []
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return [_finding("C01", "critical", path, 1, path, "This file is not UTF-8 text.")]
    if suffix in _CODE_EXT:
        return scan_code(path, text, data)
    return scan_text(path, text)
