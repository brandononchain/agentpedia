from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    path: str
    line: int
    evidence: str
    message: str
    remediation: str
    cwe: str
    owasp: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "ruleId": self.rule_id,
            "severity": self.severity,
            "path": self.path,
            "line": self.line,
            "evidence": self.evidence,
            "message": self.message,
            "remediation": self.remediation,
            "cwe": self.cwe,
            "owasp": list(self.owasp),
        }


@dataclass(frozen=True)
class Rule:
    id: str
    family: str
    severity: str
    summary: str
    remediation: str
    cwe: str
    owasp: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "family": self.family,
            "severity": self.severity,
            "summary": self.summary,
            "remediation": self.remediation,
            "cwe": self.cwe,
            "owasp": list(self.owasp),
        }


def show_evidence(text: str, limit: int = 180) -> str:
    """ASCII-safe snippet. Hidden characters are escaped so a page cannot render them."""
    out: list[str] = []
    for char in text:
        code = ord(char)
        if char in "\n\r\t":
            out.append(" ")
        elif code < 32 or code == 0xFEFF or 0xE0000 <= code <= 0xE007F or char in "\u200b\u200c\u200d\u2060\u180e\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069":
            out.append(f"\\u{code:04x}")
        else:
            out.append(char)
    collapsed = " ".join("".join(out).split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 1] + "…"
