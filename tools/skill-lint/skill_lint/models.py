from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


SEVERITIES = ("error", "warn", "info")


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    message: str
    hint: str
    path: str
    line: int | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data


@dataclass
class SkillReport:
    path: str
    name: str | None
    findings: list[Finding] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "error")

    @property
    def warn_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "warn")

    @property
    def info_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "info")


@dataclass
class LintResult:
    skills: list[SkillReport] = field(default_factory=list)
    extra_findings: list[Finding] = field(default_factory=list)

    @property
    def findings(self) -> list[Finding]:
        out = list(self.extra_findings)
        for skill in self.skills:
            out.extend(skill.findings)
        return out

    @property
    def error_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "error")

    @property
    def warn_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "warn")

    @property
    def info_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == "info")

    def to_dict(self) -> dict[str, Any]:
        return {
            "skills": [
                {
                    "path": s.path,
                    "name": s.name,
                    "findings": [f.to_dict() for f in s.findings],
                }
                for s in self.skills
            ],
            "findings": [f.to_dict() for f in self.findings],
            "summary": {
                "skills": len(self.skills),
                "errors": self.error_count,
                "warnings": self.warn_count,
                "info": self.info_count,
            },
        }
