"""Tokenizer shared by the Brain index.

The TypeScript query tokenizer in src/lib/brain/tokenize.ts must match
tokenize() here. tools/tests/brain_tokens.json locks the cases.
"""

from __future__ import annotations

import re

# Longest alias first so "pull requests" wins over "pr" and "configs" over "config".
SYNONYMS: tuple[tuple[str, str], ...] = (
    ("pull requests", "pull request"),
    ("large language models", "large language model"),
    ("model context protocol", "model context protocol"),
    ("continuous integration", "continuous integration"),
    ("continuous delivery", "continuous delivery"),
    ("semantic versioning", "semantic version"),
    ("non disclosure agreement", "non disclosure agreement"),
    ("user experience", "user experience"),
    ("user interface", "user interface"),
    ("pull request", "pull request"),
    ("semantic version", "semantic version"),
    ("large language model", "large language model"),
    ("non disclosure", "non disclosure"),
    ("prs", "pull request"),
    ("llms", "large language model"),
    ("configs", "configuration"),
    ("repos", "repository"),
    ("k8s", "kubernetes"),
    ("kube", "kubernetes"),
    ("semver", "semantic version"),
    ("soc2", "soc 2"),
    ("a11y", "accessibility"),
    ("i18n", "internationalization"),
    ("nda", "non disclosure agreement"),
    ("mcp", "model context protocol"),
    ("llm", "large language model"),
    ("yml", "yaml"),
    ("auth", "authentication"),
    ("config", "configuration"),
    ("repo", "repository"),
    ("docs", "documentation"),
    ("doc", "documentation"),
    ("pr", "pull request"),
    ("js", "javascript"),
    ("ts", "typescript"),
    ("py", "python"),
    ("gh", "github"),
    ("ci", "continuous integration"),
    ("cd", "continuous delivery"),
    ("ux", "user experience"),
    ("ui", "user interface"),
)

STOP = frozenset(
    {
        "a",
        "an",
        "the",
        "of",
        "to",
        "for",
        "and",
        "or",
        "in",
        "on",
        "with",
        "from",
        "by",
        "at",
        "as",
        "is",
        "are",
        "be",
        "this",
        "that",
        "it",
        "when",
        "how",
        "what",
        "use",
        "using",
        "used",
        "into",
        "over",
        "than",
        "then",
        "not",
        "do",
        "does",
        "their",
        "they",
        "them",
        "its",
        "if",
        "but",
        "about",
        "each",
        "per",
        "via",
        "your",
        "you",
        "we",
        "our",
        "can",
        "may",
        "should",
        "would",
        "will",
        "just",
        "also",
        "only",
        "one",
        "out",
        "up",
        "who",
        "which",
        "where",
        "why",
    }
)

_NON_ALNUM = re.compile(r"[^a-z0-9]+")
_SYNONYM_RES = tuple(
    (re.compile(r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])"), canonical)
    for alias, canonical in SYNONYMS
)


def stem(word: str) -> str:
    """Light suffix stem. Idempotent on the tokens this tokenizer emits."""
    if word in {"kubernetes", "javascript", "typescript"}:
        return word
    if len(word) < 4:
        return word
    if word.endswith("ies") and len(word) > 4:
        return word[:-3] + "y"
    if word.endswith("ing") and len(word) > 6:
        trimmed = word[:-3]
        if len(trimmed) >= 4:
            return trimmed
    if word.endswith("ed") and len(word) > 4:
        trimmed = word[:-2]
        if len(trimmed) >= 3:
            return trimmed
    if word.endswith(("sses", "shes", "ches", "xes", "zes")) and len(word) > 4:
        return word[:-2]
    if word.endswith("s") and len(word) > 4 and not word.endswith(("ss", "us", "is", "ous")):
        return word[:-1]
    return word


def tokenize(text: str) -> list[str]:
    lowered = text.lower()
    spaced = _NON_ALNUM.sub(" ", lowered)
    spaced = " ".join(spaced.split())
    for pattern, canonical in _SYNONYM_RES:
        spaced = pattern.sub(canonical, spaced)
    tokens: list[str] = []
    for word in spaced.split():
        if not word or word in STOP:
            continue
        tokens.append(stem(word))
    return tokens


EXCLUDED_AUDIT = frozenset({"on-hold", "revoked"})
EXCLUDED_CERT = frozenset({"on-hold", "withheld", "revoked"})


def servable(audit: dict | None, cert_status: str | None, digest: str | None) -> bool:
    """On-hold, revoked, withheld, and grade F never enter the index."""
    if not audit or not digest:
        return False
    grade = str(audit.get("grade") or "")
    status = str(audit.get("status") or "")
    if grade == "F" or status in EXCLUDED_AUDIT:
        return False
    if cert_status in EXCLUDED_CERT:
        return False
    return grade in {"A", "B", "C", "D"} and status in {"passed", "warning"}
