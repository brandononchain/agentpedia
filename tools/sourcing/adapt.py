"""Turn an upstream SKILL.md into one Agentpedia entry.

The result is one job, in the catalog's voice, with the upstream telemetry and
install pings removed. Attribution stays in the frontmatter for the book page.
"""

from __future__ import annotations

import re
import textwrap
from datetime import date

CURATOR = "Brandon"
CURATOR_URL = "https://github.com/brandononchain"

# Shelf keyword weights. The first matching subshelf hint wins inside a shelf.
SHELF_KEYWORDS: dict[str, list[tuple[str, int]]] = {
    "education": [("lesson", 5), ("tutorial", 5), ("curriculum", 5), ("teach", 3), ("study", 3), ("flashcard", 4)],
    "product": [("prd", 5), ("roadmap", 5), ("user research", 4), ("spec", 4), ("requirement", 3)],
    "people": [("interview", 5), ("hiring", 5), ("recruit", 5), ("onboarding", 4), ("resume", 3)],
    "docs-writing": [("readme", 3), ("documentation", 4), ("adr", 3)],
    "dev-tools": [("commit", 3), ("pull request", 3), ("refactor", 2), ("debug", 3)],
}

SUBSHELF_HINTS: dict[str, list[tuple[str, tuple[str, ...]]]] = {
    "education": [
        ("assessment", ("quiz", "exam", "grade", "assess")),
        ("practice", ("flashcard", "drill", "practice", "exercise")),
        ("lessons", ("lesson", "tutorial", "teach", "study", "curriculum", "comment")),
    ],
    "product": [
        ("roadmaps", ("roadmap",)),
        ("discovery", ("research", "interview", "discovery", "synthe", "insight")),
        ("specs", ("prd", "spec", "requirement", "feature")),
    ],
    "people": [
        ("interviews", ("interview",)),
        ("feedback", ("feedback", "performance review", "debrief")),
        ("roles", ("hiring", "recruit", "onboard", "job description", "pipeline", "headcount")),
    ],
}

_TELEMETRY = re.compile(
    r"(?i)(posthog|segment\.io|segment\.com|sentry\.io|telemetry|phone[- ]home|"
    r"googletagmanager|google-analytics|analytics\.google|webhook\.site|"
    r"npx\s+skills\s+add|curl\s+[^\n|]*\|\s*(?:sudo\s+)?(?:ba)?sh\b)"
)
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
_ZERO_WIDTH = re.compile(r"[\u200b\u200c\u200d\u2060\ufeff\u180e]")
_OVERRIDE = re.compile(
    r"(?i)ignore (?:all |any )?(?:previous|prior|above) (?:instructions|prompts)|"
    r"disregard (?:all |any )?(?:previous|prior)"
)
_YOU = re.compile(r"\b(you should|you can|you must|you|your|we|we'll|i'll|i am|i'm)\b", re.IGNORECASE)
_FENCE = re.compile(r"```.*?```", re.DOTALL)
_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def guess_shelf(name: str, description: str, path: str = "") -> str:
    text = f"{name} {description} {path}".lower().replace("_", "-")
    best = "dev-tools"
    best_score = 0
    for shelf, pairs in SHELF_KEYWORDS.items():
        score = sum(weight for word, weight in pairs if word in text)
        if score > best_score:
            best, best_score = shelf, score
    return best


def choose_subshelf(shelf: str, name: str, description: str, path: str, allowed: list[str]) -> str:
    if not allowed:
        return ""
    text = f"{name} {description} {path}".lower()
    for slug, hints in SUBSHELF_HINTS.get(shelf, []):
        if slug in allowed and any(hint in text for hint in hints):
            return slug
    return allowed[0]


_COPYRIGHT_LINE = re.compile(
    r"^\s*Copyright(?:\s+\(c\))?\s+(?:(?:19|20)\d{2}(?:\s*[-–,]\s*(?:(?:19|20)\d{2})?)?\s+)?(.+?)\s*$"
)


def _holder_from_notice(line: str) -> str:
    """Holder from a line that begins with Copyright. Empty for boilerplate."""
    match = _COPYRIGHT_LINE.match(line.strip())
    if not match:
        return ""
    holder = match.group(1).strip()
    lowered = holder.lower()
    if not holder or len(holder) > 80:
        return ""
    if any(token in lowered for token in ("[", "yyyy", "name of copyright", "all rights reserved")):
        return ""
    if lowered.startswith(("notice", "owner", "license", "the work")):
        return ""
    return holder


def copyright_line_from(license_text: str, author: str) -> str:
    """The LICENSE copyright line when it is a real notice, else a line naming the author."""
    for line in license_text.splitlines():
        holder = _holder_from_notice(line)
        if holder:
            cleaned = " ".join(line.split())
            return cleaned
    return f"Copyright {author}"


def copyright_holder(license_text: str) -> str:
    """First stated copyright holder. Skip Apache boilerplate and mid-sentence uses of the word."""
    if not license_text:
        return ""
    for line in license_text.splitlines():
        holder = _holder_from_notice(line)
        if holder:
            if holder.endswith(".") and not holder.endswith("Inc."):
                holder = holder[:-1].strip()
            return holder
    return ""


def resolve_author(owner_login: str, owner_type: str, profile_name: str, license_text: str, frontmatter_author: str) -> tuple[str, str, str]:
    """Return (display name, profile URL, person|organization).

    A GitHub profile name or a LICENSE copyright line is a stated name.
    When neither is present, the login is used. A personal name is never inferred.
    """
    login = owner_login.strip()
    url = f"https://github.com/{login}" if login else ""
    kind = "organization" if owner_type.lower() == "organization" else "person"
    stated = _short_name(frontmatter_author) or copyright_holder(license_text)
    if stated:
        return stated, url, kind
    profile = _short_name(profile_name)
    if profile:
        return profile, url, kind
    return login or "unknown", url, kind


def _short_name(value: str) -> str:
    text = " ".join(value.replace("\n", " ").split()).strip().strip("\"'")
    if not text or len(text) > 80:
        return ""
    if " " in text and len(text.split()) > 6:
        return ""
    if text.lower() in {"unknown", "n/a", "none", "the authors", "contributors"}:
        return ""
    return text


def _wrap_description(description: str) -> str:
    lines = textwrap.wrap(description.strip(), width=78) or [description.strip()]
    return "description: >-\n" + "\n".join(f"  {line}" for line in lines)


def clean_description(name: str, upstream: str) -> str:
    text = " ".join(upstream.replace("\n", " ").split())
    text = _ZERO_WIDTH.sub("", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\b(you're|you'll|you've|i'm|i'll|we're|we'll)\b", "the user", text, flags=re.IGNORECASE)
    text = _YOU.sub("the user", text)
    text = text.replace("  ", " ").strip(" .")
    if text.lower().startswith("the user"):
        text = text[0].upper() + text[1:]
    readable = name.replace("-", " ")
    if not text or len(text) < 40:
        text = f"Prepares {readable} work from the material the user supplies"
    if "when" not in text.lower():
        text = text.rstrip(".") + f". Use when the user asks for a {readable}."
    elif not re.search(r"\buse when\b", text, re.I):
        text = text.rstrip(".") + "."
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > 320:
        text = text[:317].rsplit(" ", 1)[0].rstrip(".,") + "."
        if "when" not in text.lower():
            text = text.rstrip(".") + f". Use when the user asks for a {readable}."
    return text


def _sanitize(body: str) -> str:
    body = _HTML_COMMENT.sub("", body)
    body = _ZERO_WIDTH.sub("", body)
    kept: list[str] = []
    for line in body.splitlines():
        if _TELEMETRY.search(line) or _OVERRIDE.search(line):
            continue
        if re.search(r"(?i)~/\.(claude|ssh|aws)|CLAUDE\.md|AGENTS\.md", line):
            continue
        kept.append(line)
    return "\n".join(kept)


_SKIP_SECTION = re.compile(r"(?i)when (not )?to use|when not\b|usage\b|connector|argument|example\b")
_PREFER_SECTION = re.compile(r"(?i)workflow|steps|phase|output|principle|structure|component|guideline|process|method|schema|plan")


def _bullet_lines(lines: list[str]) -> list[str]:
    found: list[str] = []
    for raw in lines:
        match = re.match(r"^\s*(?:\d+\.|[-*])\s+(.+)$", raw)
        if not match:
            continue
        line = _LINK.sub(r"\1", match.group(1))
        line = re.sub(r"[*`#>]+", "", line)
        line = " ".join(line.split()).strip()
        if len(line) < 24 or len(line) > 220:
            continue
        if _TELEMETRY.search(line) or _OVERRIDE.search(line):
            continue
        if line.lower().startswith("http"):
            continue
        found.append(line[0].upper() + line[1:] if line[0].islower() else line)
    return found


def _steps_from_body(body: str) -> list[str]:
    plain = _FENCE.sub("", body)
    sections: list[tuple[str, list[str]]] = []
    title = ""
    buf: list[str] = []
    for line in plain.splitlines():
        heading = re.match(r"^#{2,3}\s+(.+)$", line)
        if heading:
            sections.append((title, buf))
            title = heading.group(1).strip()
            buf = []
        else:
            buf.append(line)
    sections.append((title, buf))
    preferred: list[str] = []
    fallback: list[str] = []
    for section_title, lines in sections:
        if _SKIP_SECTION.search(section_title):
            continue
        bullets = _bullet_lines(lines)
        if not bullets:
            continue
        if _PREFER_SECTION.search(section_title):
            preferred.extend(bullets)
        else:
            fallback.extend(bullets)
    return (preferred or fallback)[:5]


def article_for(text: str) -> str:
    return "an" if text[:1].lower() in "aeiou" else "a"


def _example_from_body(body: str, readable: str) -> str:
    match = re.search(r"(?ims)^##\s+example\b.*?(?=^##\s|\Z)", body)
    if not match:
        return (
            f"User: Draft {article_for(readable)} {readable} from the notes in this message. Leave any figure I did not state as unknown.\n\n"
            f"Agent: A short {readable} that uses only those notes, names the gaps, and points at the check that would show it is done."
        )
    chunk = _FENCE.sub("", match.group(0))
    chunk = re.sub(r"(?m)^##.*$", "", chunk)
    chunk = _LINK.sub(r"\1", chunk)
    lines = [" ".join(line.split()) for line in chunk.splitlines() if line.strip()]
    snippet = " ".join(lines[:4]).strip()
    if len(snippet) < 40:
        return (
            f"User: Draft {article_for(readable)} {readable} from the notes in this message.\n\n"
            f"Agent: A short {readable} that quotes only the notes and marks everything else unknown."
        )
    if len(snippet) > 420:
        snippet = snippet[:417].rsplit(" ", 1)[0] + "."
    return f"User: Use the case below as the source material for {article_for(readable)} {readable}.\n\n{snippet}\n\nAgent: A draft that keeps those facts and leaves out anything the case did not state."


def render_skill(
    *,
    name: str,
    description: str,
    shelf: str,
    subshelf: str,
    tags: str,
    added: str,
    author: str,
    author_url: str,
    author_kind: str,
    license_id: str,
    repo: str,
    commit: str,
    upstream_path: str,
    copyright_line: str,
    steps: list[str],
    example: str,
) -> str:
    readable = name.replace("-", " ")
    numbered = [
        "Confirm the inputs the user actually supplied. Ask about a missing fact instead of inventing it.",
        *steps[:5],
        "Validate the draft against that list: every claim traces to the user, and the gaps stay labeled unknown.",
    ]
    # Keep the list short and unique.
    seen: set[str] = set()
    cleaned_steps: list[str] = []
    for step in numbered:
        key = step.lower()
        if key in seen:
            continue
        seen.add(key)
        cleaned_steps.append(step)
    step_lines = "\n".join(f"{index}. {step}" for index, step in enumerate(cleaned_steps, start=1))
    title = readable[:1].upper() + readable[1:]
    body = f"""# {title}

Do this one job: {article_for(readable)} {readable}. Adapted from `{repo}` at commit `{commit[:12]}` ({license_id}). {copyright_line}

## Steps

{step_lines}

## Example

{example.strip()}

## Boundaries

Do not publish the result, send it, or delete anything. Show the draft and wait. Do not install packages or phone a vendor. This skill does not invent metrics, people, or files the user did not provide.
"""
    meta = [
        "---",
        f"name: {name}",
        _wrap_description(description),
        f"license: {license_id}",
        "metadata:",
        f"  category: {shelf}",
        f"  subshelf: {subshelf}",
        f"  tags: {tags}",
        f'  added: "{added}"',
        "  featured: false",
        "  source: import",
        f"  author: {_yaml_quote(author)}",
        f"  authorUrl: {_yaml_quote(author_url)}",
        f"  authorKind: {author_kind if author_kind in {'person', 'organization'} else 'person'}",
        f"  curator: {CURATOR}",
        f"  upstream: {_yaml_quote(repo)}",
        f"  upstreamCommit: {commit}",
        f"  upstreamPath: {_yaml_quote(upstream_path)}",
        f"  upstreamLicense: {_yaml_quote(license_id)}",
        f"  copyright: {_yaml_quote(copyright_line)}",
        "---",
        "",
        body.rstrip(),
        "",
    ]
    return "\n".join(meta)


def _yaml_quote(value: str) -> str:
    text = value.replace('"', "'").strip()
    if not text:
        return '""'
    if any(char in text for char in ":#{}[],&*!|>%@`") or text.lower() in {"yes", "no", "true", "false"}:
        return f'"{text}"'
    return text


def tags_for(name: str, shelf: str) -> str:
    parts = [part for part in name.split("-") if part and part not in {"a", "the", "and"}]
    words = parts[:3] or [shelf]
    if shelf not in words:
        words.append(shelf.split("-")[0])
    return ", ".join(words[:4])


def adapt_skill(
    *,
    name: str,
    upstream_text: str,
    description: str,
    shelf: str,
    subshelf: str,
    author: str,
    author_url: str,
    author_kind: str,
    license_id: str,
    repo: str,
    commit: str,
    upstream_path: str,
    copyright_line: str,
    added: str | None = None,
) -> str:
    body = _sanitize(upstream_text)
    # Drop upstream frontmatter from the body search.
    if body.startswith("---"):
        end = body.find("\n---", 3)
        if end != -1:
            body = body[end + 4 :]
    readable = name.replace("-", " ")
    steps = _steps_from_body(body)
    if not steps:
        steps = [
            f"Restate the {readable} in one sentence using the user's words.",
            "List the decisions, the non-goals, and the check that would show the work is done.",
        ]
    example = _example_from_body(body, readable)
    # The synthesized example says "I did not" which is the user's line. That is fine in the body.
    # Strip a first-person agent voice if the example starts with I as the agent.
    return render_skill(
        name=name,
        description=clean_description(name, description),
        shelf=shelf,
        subshelf=subshelf,
        tags=tags_for(name, shelf),
        added=added or date.today().isoformat(),
        author=author,
        author_url=author_url,
        author_kind=author_kind,
        license_id=license_id,
        repo=repo,
        commit=commit,
        upstream_path=upstream_path,
        copyright_line=copyright_line or f"Copyright {author}",
        steps=steps,
        example=example,
    )
