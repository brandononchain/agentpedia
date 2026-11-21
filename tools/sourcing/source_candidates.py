#!/usr/bin/env python3
"""Discover public Agent Skill (SKILL.md) and agent-repo candidates for Agentpedia.

Reads the Agentpedia catalog for duplicate checks, then gathers real candidates
from GitHub (gh CLI when available, otherwise the public API), known skill
collections, awesome lists, skills.sh search, and a small set of verified web
mentions. Writes a ranked queue as CSV and Markdown.

Every source URL is taken from a live API or page. Candidates whose URLs fail a
spot-check are marked unreachable rather than invented.

The default catalog is data/catalog.json. The queue is written to
data/candidates.json (generated). Pass --from-snapshot to compact an existing
full snapshot without calling GitHub again.

Usage:
  python3 tools/sourcing/source_candidates.py
  python3 tools/sourcing/source_candidates.py --from-snapshot candidates.json
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

USER_AGENT = "agentpedia-sourcing/1.0 (+https://agentpedia.sh; research bot for catalog sourcing)"
GITHUB_API = "https://api.github.com"
SKILLS_SH_SEARCH = "https://skills.sh/api/search"
RAW_GH = "https://raw.githubusercontent.com"

# Permissive licenses that can be adapted into Apache-2.0 Agentpedia entries
# with attribution. Copyleft is kept in the queue but marked review-required.
COMPATIBLE = {
    "mit",
    "apache-2.0",
    "apache-2.0-readme",
    "bsd-2-clause",
    "bsd-3-clause",
    "bsd-3-clause-clear",
    "isc",
    "0bsd",
    "unlicense",
    "cc0-1.0",
    "cc-by-4.0",
    "cc-by-3.0",
    "blueoak-1.0.0",
    "python-2.0",
    "zlib",
    "artistic-2.0",
}
COPYLEFT = {
    "gpl-2.0",
    "gpl-3.0",
    "agpl-3.0",
    "lgpl-2.1",
    "lgpl-3.0",
    "mpl-2.0",
    "cc-by-sa-4.0",
    "cc-by-sa-3.0",
    "epl-2.0",
    "eupl-1.2",
}

# Official or clearly maintained collections to walk for SKILL.md files.
KNOWN_COLLECTIONS = [
    "anthropics/skills",
    "vercel-labs/agent-skills",
    "vercel-labs/skills",
    "obra/superpowers",
    "obsidianmd/obsidian-skills",
    "addyosmani/agent-skills",
    "pbakaus/impeccable",
    "google/skills",
    "github/awesome-copilot",
    "cloudflare/security-audit-skill",
    "K-Dense-AI/scientific-agent-skills",
    "phuryn/pm-skills",
    "wshobson/agents",
    "googleworkspace/cli",
    "Leonxlnx/taste-skill",
    "tt-a1i/archify",
    "blader/humanizer",
    "mvanhorn/last30days-skill",
    "OthmanAdi/planning-with-files",
    "latent-spaces/brag",
    "Vincentwei1021/video-shotcraft",
    "wheresryan22/anatomy",
    "JimLiu/baoyu-skills",
    "alirezarezvani/claude-skills",
]

AWESOME_LISTS = [
    "VoltAgent/awesome-agent-skills",
    "ComposioHQ/awesome-claude-skills",
    "travisvn/awesome-claude-skills",
    "BehiSecc/awesome-claude-skills",
    "heilcheng/awesome-agent-skills",
    "hesreallyhim/awesome-claude-code",
]

# Diverse skills.sh queries so we are not stuck on one topic. The public
# search endpoint returns up to 100 hits and requires a query of 2+ chars.
SKILLS_SH_QUERIES = [
    "pdf", "git", "react", "skill", "test", "docs", "security", "docker",
    "kubernetes", "aws", "sql", "python", "review", "design", "frontend",
    "research", "writing", "market", "finance", "legal", "sales", "support",
    "video", "image", "plan", "meeting", "email", "calendar", "lesson",
    "hiring", "interview", "resume", "roadmap", "product", "seo", "deploy",
    "lint", "debug", "api", "changelog", "obsidian", "pptx", "xlsx",
    "eval", "mcp", "prompt", "trading", "crypto", "invoice", "accessibility",
    "onboarding", "curriculum", "science", "biology", "prd", "figma",
]

# Verified public web mentions (fetched during this run's research). These are
# not X API results; Grok Bot X tools were unavailable to this script, so we
# record durable public pages instead of inventing tweet URLs.
WEB_MENTIONS = [
    {
        "name": "x",
        "url": "https://docs.x.com",
        "notes": "Official X agent skill; install with `npx skills add https://docs.x.com --skill x` (documented by twitterapi.io and skillzs.dev).",
        "discovery_source": "web-docs",
    },
]

# Shelf keyword weights. Higher weight wins. Education, Product, and People
# are currently empty on Agentpedia and get a ranking bonus later.
SHELF_KEYWORDS: dict[str, list[tuple[str, int]]] = {
    "skill-authoring": [
        ("skill-creator", 5), ("skill creator", 5), ("write a skill", 5),
        ("author a skill", 5), ("agent skills spec", 3),
        ("docs-to-skill", 4),
    ],
    "agent-ops": [
        ("eval", 3), ("benchmark", 3), ("mcp", 3), ("trace", 2),
        ("agent ops", 4), ("prompt injection", 3), ("agent eval", 4),
    ],
    "dev-tools": [
        ("git commit", 4), ("pull request", 4), ("pr review", 5),
        ("code review", 4), ("changelog", 3), ("semver", 4), ("unit test", 3),
        ("tdd", 3), ("debugger", 3), ("refactor", 2), ("lint", 2),
        ("conventional commit", 4), ("git worktree", 4), ("systematic debugging", 5), ("debugging", 3),
        ("test-driven", 4), ("code review", 4),
    ],
    "devops-cloud": [
        ("docker", 4), ("kubernetes", 5), ("github actions", 4), ("terraform", 4),
        ("deploy", 3), ("ci/cd", 4), ("aws", 3), ("gcp", 3), ("azure", 3),
        ("dockerfile", 4), ("helm", 3), ("cloudflare", 3),
        ("firmware", 4), ("esp32", 5), ("gke", 4), ("google cloud", 4),
    ],
    "security-compliance": [
        ("security audit", 5), ("vulnerability", 4), ("secret scan", 4),
        ("owasp", 4), ("soc 2", 4), ("soc2", 4), ("compliance", 3),
        ("cve", 3), ("sast", 3), ("authentication", 2),
    ],
    "data-engineering": [
        ("etl", 4), ("dbt", 5), ("airflow", 4), ("data pipeline", 4),
        ("schema", 3), ("warehouse", 3), ("spark", 3), ("kafka", 3),
    ],
    "data-analysis": [
        ("pandas", 4), ("data analysis", 4), ("statistics", 3), ("csv", 2),
        ("metric", 2), ("notebook", 2), ("visualization", 2), ("sql query", 3),
    ],
    "web-research": [
        ("web research", 5), ("citation", 3), ("source brief", 4),
        ("literature review", 4), ("osint", 3), ("last 30 days", 4),
        ("search the web", 3),
    ],
    "docs-writing": [
        ("readme", 3), ("documentation", 4), ("api doc", 4), ("adr", 3),
        ("release notes", 3), ("technical writing", 4), ("style guide", 2),
    ],
    "design-frontend": [
        ("react", 3), ("next.js", 3), ("css", 2), ("ui review", 4),
        ("frontend", 3), ("figma", 4), ("accessibility", 4), ("a11y", 4),
        ("design system", 4), ("web design", 4), ("art direction", 4),
        ("taste", 2),
    ],
    "trading": [
        ("trading", 5), ("backtest", 4), ("options", 2), ("equity", 2),
        ("position risk", 4), ("market data", 3),
    ],
    "crypto-onchain": [
        ("solidity", 5), ("blockchain", 4), ("crypto", 3), ("wallet", 3),
        ("ethereum", 4), ("smart contract", 4), ("onchain", 4),
    ],
    "finance-ops": [
        ("invoice", 4), ("bookkeep", 4), ("accounting", 4), ("forecast", 3),
        ("expense", 3), ("payroll", 3), ("budget", 2),
    ],
    "legal-contracts": [
        ("contract review", 5), ("nda", 4), ("legal", 3), ("clause", 3),
        ("redline", 4), ("terms of service", 3),
    ],
    "sales-gtm": [
        ("outbound", 4), ("sales", 3), ("gtm", 4), ("objection", 4),
        ("discovery call", 5), ("prospect", 4), ("pipeline", 1),
    ],
    "marketing": [
        ("marketing", 4), ("seo", 4), ("content calendar", 4), ("launch post", 4),
        ("copywriting", 3), ("social media", 3), ("twitter", 2),
    ],
    "customer-support": [
        ("customer support", 5), ("ticket triage", 5), ("help center", 4),
        ("kb article", 4), ("support reply", 4),
    ],
    "media-content": [
        ("video", 3), ("subtitle", 4), ("thumbnail", 4), ("podcast", 3),
        ("pptx", 3), ("powerpoint", 3), ("slide", 3), ("image gen", 3),
        ("remotion", 4), ("ffmpeg", 3),
    ],
    "productivity": [
        ("daily plan", 4), ("inbox", 3), ("todo", 3), ("meeting notes", 4),
        ("calendar", 3), ("planning with files", 5),
    ],
    "personal-life": [
        ("health", 2), ("travel", 3), ("trip plan", 4), ("home week", 4),
        ("family", 2), ("habit", 2),
    ],
    "education": [
        ("lesson plan", 5), ("curriculum", 5), ("tutor", 4), ("teach", 3),
        ("course", 3), ("classroom", 4), ("student", 3), ("biology", 3),
        ("chemistry", 3), ("scientific", 3), ("science", 2),
    ],
    "product": [
        ("product manager", 5), ("prd", 5), ("roadmap", 5), ("user research", 4),
        ("prioritiz", 4), ("sprint planning", 4), ("product discovery", 5),
        ("opportunity brief", 4), ("pm skill", 4),
    ],
    "people": [
        ("hiring", 5), ("interview", 4), ("job description", 5), ("resume", 3),
        ("recruiter", 4), ("new hire", 5), ("employee onboarding", 5),
        ("onboarding checklist", 5), ("performance review", 5),
        ("headcount", 4), ("compensation", 3),
    ],
}

EMPTY_SHELVES = {"education", "product", "people"}

OFFICIAL_ORGS = {
    "anthropics", "vercel-labs", "google", "github", "obsidianmd",
    "cloudflare", "NVIDIA", "googleworkspace", "obra", "addyosmani",
    "agentskills",
}

# Repos that look like bulk-generated catalogs; keep them but cap ranking.
BULK_HINTS = ("3000+", "1000+", "410 ", "awesome-llm", "agentic-awesome")

SKIP_PATH_PARTS = {
    "node_modules", ".git", "vendor", "dist", "build", "__pycache__",
    "fixtures", "testdata", "test-fixtures",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def slug(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-{2,}", "-", s).strip("-")


def normalize_name(name: str) -> str:
    n = slug(name)
    for prefix in (
        "vercel-", "anthropic-", "anthropics-", "google-", "obsidian-",
        "claude-", "codex-", "cursor-", "agent-", "skill-",
    ):
        if n.startswith(prefix) and len(n) > len(prefix) + 2:
            n = n[len(prefix):]
    return n


def parse_frontmatter(text: str) -> dict[str, str]:
    """Minimal YAML frontmatter parser for SKILL.md name/description/license."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    block = text[3:end].strip()
    data: dict[str, str] = {}
    key: str | None = None
    acc: list[str] = []

    def flush() -> None:
        nonlocal key, acc
        if key:
            data[key] = "\n".join(acc).strip().strip("\"'")
        key, acc = None, []

    for line in block.splitlines():
        m = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if m and not line.startswith(" "):
            flush()
            key = m.group(1).strip()
            rest = m.group(2).strip()
            if rest in ("|", ">", ">-", "|-"):
                acc = []
            else:
                acc = [rest]
        elif key:
            acc.append(line.strip())
    flush()
    return data


def classify_license(raw: str | None) -> tuple[str, str]:
    """Return (spdx_or_label, status) where status is compatible, copyleft, unknown, none."""
    if not raw:
        return "unknown", "unknown"
    s = raw.strip()
    low = s.lower().replace(" ", "")
    # normalize common phrases
    if "apache" in low and "2" in low:
        key = "apache-2.0"
    elif low in {"mit", "mitlicense"} or low.startswith("mit"):
        key = "mit"
    elif "bsd-3" in low or "bsd3" in low or "3-clause" in low:
        key = "bsd-3-clause"
    elif "bsd-2" in low or "bsd2" in low or "2-clause" in low:
        key = "bsd-2-clause"
    elif low in {"isc"}:
        key = "isc"
    elif "cc0" in low:
        key = "cc0-1.0"
    elif "cc-by-sa" in low or "ccbysa" in low:
        key = "cc-by-sa-4.0"
    elif "cc-by" in low or "ccby" in low:
        key = "cc-by-4.0"
    elif "agpl" in low:
        key = "agpl-3.0"
    elif "lgpl" in low:
        key = "lgpl-3.0"
    elif "gpl-3" in low or "gpl3" in low or low == "gplv3":
        key = "gpl-3.0"
    elif "gpl-2" in low or "gpl2" in low:
        key = "gpl-2.0"
    elif "unlicense" in low:
        key = "unlicense"
    elif "mpl" in low:
        key = "mpl-2.0"
    else:
        key = low.strip("-") or "unknown"

    # README-stated licenses without a GitHub-detected file. The importer
    # will not copy these until a LICENSE file is present.
    if "readme" in low and "apache" in low:
        return "Apache-2.0", "readme-only"
    if "readme" in low and "mit" in low:
        return "MIT", "readme-only"

    if key in COMPATIBLE:
        return key, "compatible"
    if key in COPYLEFT:
        return key, "copyleft"
    if key in {"unknown", "other", "noassertion", "none", ""}:
        return "unknown", "unknown"
    return s, "unknown"


def guess_shelf(name: str, description: str, path: str = "") -> tuple[str, int]:
    text = f"{name} {description} {path}".lower().replace("_", "-")
    scores: dict[str, int] = defaultdict(int)
    for shelf, kws in SHELF_KEYWORDS.items():
        for kw, w in kws:
            if kw in text:
                scores[shelf] += w
    if not scores:
        return "dev-tools", 0
    shelf = max(scores, key=lambda k: (scores[k], -list(SHELF_KEYWORDS).index(k)))
    return shelf, scores[shelf]


@dataclass
class Candidate:
    name: str
    source_url: str
    repo: str = ""
    skill_path: str = ""
    license: str = "unknown"
    license_status: str = "unknown"
    stars: int = 0
    last_commit: str = ""
    description: str = ""
    guessed_shelf: str = ""
    shelf_confidence: int = 0
    installs: int = 0
    already_in_catalog: bool = False
    catalog_match: str = ""
    discovery_source: str = ""
    default_branch: str = "main"
    rank_score: float = 0.0
    notes: str = ""
    verified_url: str = ""

    def key(self) -> str:
        return f"{self.repo.lower()}::{slug(self.name)}::{self.skill_path.lower()}"


class Cache:
    def __init__(self, root: Path):
        self.root = root
        root.mkdir(parents=True, exist_ok=True)

    def _path(self, namespace: str, key: str) -> Path:
        safe = re.sub(r"[^A-Za-z0-9._/@-]+", "_", key).replace("/", "__")
        if len(safe) > 180:
            safe = safe[:140] + "_" + str(abs(hash(key)))
        d = self.root / namespace
        d.mkdir(exist_ok=True)
        return d / f"{safe}.json"

    def get(self, namespace: str, key: str) -> Any | None:
        p = self._path(namespace, key)
        if p.exists():
            try:
                return json.loads(p.read_text())
            except json.JSONDecodeError:
                return None
        return None

    def set(self, namespace: str, key: str, value: Any) -> None:
        p = self._path(namespace, key)
        p.write_text(json.dumps(value, indent=None))


class Http:
    def __init__(self, cache: Cache, min_interval: float = 0.15):
        self.cache = cache
        self.min_interval = min_interval
        self._last = 0.0
        self.token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
        self.gh = shutil.which("gh")

    def _sleep(self) -> None:
        dt = time.monotonic() - self._last
        if dt < self.min_interval:
            time.sleep(self.min_interval - dt)
        self._last = time.monotonic()

    def fetch(self, url: str, headers: dict[str, str] | None = None, cache_ns: str = "http", retries: int = 4) -> tuple[int, bytes, str]:
        cached = self.cache.get(cache_ns, url)
        if cached and cached.get("status") in range(200, 300):
            return cached["status"], cached["body"].encode("utf-8") if isinstance(cached["body"], str) else bytes(cached["body"]), cached.get("final_url", url)

        hdrs = {"User-Agent": USER_AGENT, "Accept": "application/json, text/plain, */*"}
        if headers:
            hdrs.update(headers)
        last_err = ""
        for attempt in range(retries):
            self._sleep()
            req = urllib.request.Request(url, headers=hdrs)
            try:
                with urllib.request.urlopen(req, timeout=25) as resp:
                    body = resp.read()
                    final = str(resp.geturl())
                    status = resp.status
                    # cache text-ish bodies as str when possible
                    try:
                        stored = body.decode("utf-8")
                    except UnicodeDecodeError:
                        stored = body.decode("utf-8", "replace")
                    self.cache.set(cache_ns, url, {"status": status, "body": stored, "final_url": final})
                    return status, body, final
            except urllib.error.HTTPError as e:
                body = e.read() if e.fp else b""
                if e.code in (429, 403, 502, 503) and attempt < retries - 1:
                    wait = 2 ** attempt + random.random()
                    log(f"  backoff {wait:.1f}s on {e.code} {url}")
                    time.sleep(wait)
                    last_err = f"{e.code}"
                    continue
                try:
                    stored = body.decode("utf-8", "replace")
                except Exception:
                    stored = ""
                if e.code in (200, 301, 302, 404, 401):
                    self.cache.set(cache_ns, url, {"status": e.code, "body": stored, "final_url": url})
                return e.code, body, url
            except Exception as e:
                last_err = str(e)
                if attempt < retries - 1:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                return 0, last_err.encode(), url
        return 0, last_err.encode(), url

    def gh_api(self, path: str, raw: bool = False) -> Any:
        path = path if path.startswith("http") else f"{GITHUB_API}/{path.lstrip('/')}"
        cache_key = ("raw:" if raw else "json:") + path
        cached = self.cache.get("gh", cache_key)
        if cached is not None:
            return cached

        if self.gh:
            cmd = ["gh", "api"]
            if raw:
                cmd += ["-H", "Accept: application/vnd.github.raw"]
            # gh wants path without host when using "gh api"
            api_path = path
            if api_path.startswith(GITHUB_API):
                api_path = api_path[len(GITHUB_API):]
            if "git/trees/" in api_path and "recursive" not in api_path:
                # allow already-queried paths
                pass
            cmd.append(api_path)
            self._sleep()
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            except subprocess.TimeoutExpired:
                return None
            if proc.returncode != 0:
                err = (proc.stderr or "") + (proc.stdout or "")
                if "404" in err or "Not Found" in err:
                    self.cache.set("gh", cache_key, None)
                    return None
                if "rate limit" in err.lower() or "403" in err:
                    log(f"  gh api issue: {err.strip()[:200]}")
                    time.sleep(8)
                return None
            if raw:
                self.cache.set("gh", cache_key, proc.stdout)
                return proc.stdout
            try:
                data = json.loads(proc.stdout) if proc.stdout else None
            except json.JSONDecodeError:
                data = proc.stdout
            self.cache.set("gh", cache_key, data)
            return data

        headers = {"User-Agent": USER_AGENT, "Accept": "application/vnd.github+json"}
        if raw:
            headers["Accept"] = "application/vnd.github.raw"
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        status, body, _ = self.fetch(path, headers=headers, cache_ns="gh-http")
        if status != 200:
            return None
        text = body.decode("utf-8", "replace")
        if raw:
            self.cache.set("gh", cache_key, text)
            return text
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            data = text
        self.cache.set("gh", cache_key, data)
        return data

    def gh_search_repos(self, query: str, limit: int = 30) -> list[dict[str, Any]]:
        if self.gh:
            self._sleep()
            proc = subprocess.run(
                [
                    "gh", "search", "repos", query, "--limit", str(limit),
                    "--sort", "stars",
                    "--json", "name,fullName,description,url,stargazersCount,license,updatedAt,defaultBranchRef",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if proc.returncode == 0 and proc.stdout:
                try:
                    return json.loads(proc.stdout)
                except json.JSONDecodeError:
                    return []
            return []
        q = urllib.parse.urlencode({"q": query, "sort": "stars", "per_page": min(limit, 30)})
        data = self.gh_api(f"{GITHUB_API}/search/repositories?{q}")
        items = (data or {}).get("items") if isinstance(data, dict) else []
        out = []
        for it in items or []:
            lic = (it.get("license") or {})
            out.append({
                "fullName": it.get("full_name"),
                "description": it.get("description") or "",
                "url": it.get("html_url"),
                "stargazersCount": it.get("stargazers_count") or 0,
                "license": {"key": lic.get("key") or "", "name": lic.get("name") or ""},
                "updatedAt": it.get("pushed_at") or it.get("updated_at") or "",
            })
        return out

    def gh_search_code(self, query: str, limit: int = 50) -> list[dict[str, Any]]:
        if self.gh:
            self._sleep()
            proc = subprocess.run(
                [
                    "gh", "search", "code", query, "--limit", str(limit),
                    "--json", "repository,path,url",
                ],
                capture_output=True,
                text=True,
                timeout=90,
            )
            if proc.returncode == 0 and proc.stdout:
                try:
                    return json.loads(proc.stdout)
                except json.JSONDecodeError:
                    return []
            return []
        q = urllib.parse.urlencode({"q": query, "per_page": min(limit, 50)})
        data = self.gh_api(f"{GITHUB_API}/search/code?{q}")
        return (data or {}).get("items") or [] if isinstance(data, dict) else []


def load_catalog(path: Path) -> tuple[dict[str, dict[str, Any]], dict[str, str], list[str]]:
    data = json.loads(path.read_text())
    by_name: dict[str, dict[str, Any]] = {}
    norm: dict[str, str] = {}
    shelves: list[str] = []
    for c in data.get("categories") or []:
        shelves.append(c.get("id"))
    for kind, rows in (("skill", data.get("skills") or []), ("agent", data.get("agents") or [])):
        for row in rows:
            name = row.get("name") or ""
            by_name[name] = {"kind": kind, **row}
            norm[normalize_name(name)] = name
            norm[slug(name)] = name
    return by_name, norm, shelves


def repo_meta(http: Http, repo: str) -> dict[str, Any]:
    data = http.gh_api(f"repos/{repo}")
    if not isinstance(data, dict) or not data.get("full_name"):
        return {}
    lic = data.get("license") or {}
    spdx = lic.get("spdx_id") or lic.get("key") or ""
    if spdx in {"NOASSERTION", "OTHER", None}:
        spdx = ""
    # README-stated fallback for known official repos without a detected file
    if not spdx:
        if repo.lower() == "anthropics/skills":
            spdx = "Apache-2.0 (README; no LICENSE file)"
        elif repo.lower() == "vercel-labs/agent-skills":
            spdx = "MIT (README; no LICENSE file)"
    return {
        "repo": data.get("full_name") or repo,
        "description": data.get("description") or "",
        "stars": int(data.get("stargazers_count") or 0),
        "license_raw": spdx or "",
        "pushed_at": data.get("pushed_at") or data.get("updated_at") or "",
        "default_branch": (data.get("default_branch") or "main"),
        "html_url": data.get("html_url") or f"https://github.com/{repo}",
        "archived": bool(data.get("archived")),
        "fork": bool(data.get("fork")),
    }


def list_skill_md(http: Http, repo: str, branch: str) -> list[str]:
    # recursive tree; one call per repo
    data = http.gh_api(f"repos/{repo}/git/trees/{urllib.parse.quote(branch)}?recursive=1")
    if not isinstance(data, dict):
        # try main/master fallback
        for b in ("main", "master"):
            if b == branch:
                continue
            data = http.gh_api(f"repos/{repo}/git/trees/{b}?recursive=1")
            if isinstance(data, dict) and data.get("tree"):
                break
    tree = (data or {}).get("tree") if isinstance(data, dict) else None
    if not tree:
        return []
    paths = []
    for node in tree:
        if node.get("type") != "blob":
            continue
        p = node.get("path") or ""
        if not p.endswith("SKILL.md") and not p.endswith("skill.md"):
            # Agentpedia requires SKILL.md; keep exact case plus lowercase for discovery
            continue
        parts = set(p.split("/"))
        if parts & SKIP_PATH_PARTS:
            continue
        paths.append(p)
    return paths


def skill_name_from_path(path: str) -> str:
    parts = path.strip("/").split("/")
    if parts[-1].lower() == "skill.md" and len(parts) >= 2:
        return slug(parts[-2])
    return slug(Path(path).stem)


def fetch_skill_frontmatter(http: Http, repo: str, branch: str, path: str) -> dict[str, str]:
    url = f"{RAW_GH}/{repo}/{branch}/{path}"
    status, body, _ = http.fetch(url, headers={"User-Agent": USER_AGENT, "Accept": "text/plain"}, cache_ns="raw")
    if status != 200:
        # try gh api raw
        text = http.gh_api(f"repos/{repo}/contents/{urllib.parse.quote(path)}?ref={urllib.parse.quote(branch)}", raw=True)
        if isinstance(text, str) and text.startswith("---"):
            return parse_frontmatter(text)
        return {}
    text = body.decode("utf-8", "replace")
    return parse_frontmatter(text)


def discover_collections(http: Http, out: dict[str, Candidate]) -> None:
    log(f"Walking {len(KNOWN_COLLECTIONS)} known collections for SKILL.md…")
    for repo in KNOWN_COLLECTIONS:
        meta = repo_meta(http, repo)
        if not meta:
            log(f"  skip {repo}: repo metadata missing")
            continue
        paths = list_skill_md(http, meta["repo"], meta["default_branch"])
        log(f"  {repo}: {len(paths)} SKILL.md, stars={meta['stars']}, license={meta['license_raw'] or 'unknown'}")
        # Cap walk-enrichment later; record all paths
        # If a collection has no SKILL.md but is itself a skill-ish repo, still record the repo
        if not paths:
            # maybe the skill is at a nonstandard location; still add the repo as a pointer
            continue
        lic_label, lic_status = classify_license(meta["license_raw"])
        for path in paths:
            name = skill_name_from_path(path)
            url = f"https://github.com/{meta['repo']}/blob/{meta['default_branch']}/{path}"
            add_candidate(
                out,
                Candidate(
                    name=name,
                    source_url=url,
                    repo=meta["repo"],
                    skill_path=path,
                    license=lic_label,
                    license_status=lic_status,
                    stars=meta["stars"],
                    last_commit=meta["pushed_at"],
                    description=meta["description"],
                    discovery_source="known-collection",
                    default_branch=meta["default_branch"],
                    notes="",
                ),
            )


def add_candidate(out: dict[str, Candidate], c: Candidate) -> None:
    if not c.name or c.repo.lower().startswith("brandononchain/agentpedia"):
        return
    k = c.key()
    if k in out:
        prev = out[k]
        # merge richer fields
        if c.installs > prev.installs:
            prev.installs = c.installs
        if c.description and (not prev.description or len(c.description) > len(prev.description)):
            prev.description = c.description
        if c.license_status == "compatible" and prev.license_status != "compatible":
            prev.license = c.license
            prev.license_status = c.license_status
        srcs = set(filter(None, (prev.discovery_source, c.discovery_source)))
        # keep unique sources
        parts = []
        for s in (prev.discovery_source + "," + c.discovery_source).split(","):
            s = s.strip()
            if s and s not in parts:
                parts.append(s)
        prev.discovery_source = ",".join(parts)
        if c.stars > prev.stars:
            prev.stars = c.stars
        return
    out[k] = c


def discover_topics_and_search(http: Http, out: dict[str, Candidate]) -> None:
    queries = [
        "topic:agent-skills",
        "topic:claude-skills",
        "topic:agent-skill",
        "SKILL.md agent skills",
        "SKILL.md in:readme license:mit",
        "SKILL.md in:readme license:apache-2.0",
    ]
    log("Searching GitHub repositories and code for SKILL.md…")
    seen_repos: set[str] = set()
    for q in queries:
        repos = http.gh_search_repos(q, limit=25)
        for r in repos:
            full = r.get("fullName") or r.get("full_name") or ""
            if not full or full in seen_repos:
                continue
            seen_repos.add(full)
            lic = r.get("license") or {}
            raw = lic.get("spdx_id") or lic.get("key") or ""
            if isinstance(raw, str) and raw.lower() in {"", "other", "noassertion"}:
                raw = ""
            label, status = classify_license(raw)
            add_candidate(
                out,
                Candidate(
                    name=full.split("/")[-1],
                    source_url=r.get("url") or f"https://github.com/{full}",
                    repo=full,
                    skill_path="",
                    license=label,
                    license_status=status,
                    stars=int(r.get("stargazersCount") or r.get("stargazers_count") or 0),
                    last_commit=r.get("updatedAt") or r.get("pushed_at") or "",
                    description=r.get("description") or "",
                    discovery_source="github-repo-search",
                ),
            )
        time.sleep(0.2)

    # Code search: filename SKILL.md
    for q in ('filename:SKILL.md', 'path:SKILL.md name: description:'):
        hits = http.gh_search_code(q, limit=40)
        log(f"  code search {q!r}: {len(hits)} hits")
        for h in hits:
            repo_obj = h.get("repository") or {}
            full = repo_obj.get("nameWithOwner") or repo_obj.get("full_name") or ""
            path = h.get("path") or "SKILL.md"
            if not full:
                continue
            url = h.get("url") or f"https://github.com/{full}/blob/HEAD/{path}"
            add_candidate(
                out,
                Candidate(
                    name=skill_name_from_path(path) if path.lower().endswith("skill.md") else slug(full.split("/")[-1]),
                    source_url=url,
                    repo=full,
                    skill_path=path if path.lower().endswith("skill.md") else "",
                    discovery_source="github-code-search",
                ),
            )


GH_REPO_RE = re.compile(
    r"https?://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)(?:/tree/[^)\s]+|/blob/[^)\s]+)?",
    re.I,
)


def discover_awesome_lists(http: Http, out: dict[str, Candidate]) -> None:
    log("Parsing awesome-list READMEs for GitHub skill links…")
    for repo in AWESOME_LISTS:
        meta = repo_meta(http, repo)
        branch = (meta or {}).get("default_branch") or "main"
        text = http.gh_api(f"repos/{repo}/contents/README.md?ref={branch}", raw=True)
        if not isinstance(text, str):
            # try lowercase
            text = http.gh_api(f"repos/{repo}/contents/readme.md?ref={branch}", raw=True)
        if not isinstance(text, str):
            log(f"  no README for {repo}")
            continue
        found = set()
        for m in GH_REPO_RE.finditer(text):
            owner, name = m.group(1), m.group(2)
            if name.lower() in {"awesome-agent-skills", "awesome-claude-skills", "awesome-claude-code", "awesome-copilot"}:
                continue
            if owner.lower() in {"topics", "site", "settings"}:
                continue
            found.add(f"{owner}/{name}")
        log(f"  {repo}: {len(found)} unique GitHub repos linked")
        # Only record the link; enrichment happens later for a ranked subset
        # To avoid exploding the queue with unverified list entries, keep repos
        # that already appeared or look like skill repos (name contains skill).
        for full in sorted(found):
            if "skill" not in full.lower() and full not in {c.repo for c in out.values()}:
                # still keep a sample of high-signal names
                if not re.search(r"(agent|claude|codex|cursor|mcp|prompt)", full.lower()):
                    continue
            add_candidate(
                out,
                Candidate(
                    name=full.split("/")[-1],
                    source_url=f"https://github.com/{full}",
                    repo=full,
                    discovery_source=f"awesome-list:{repo}",
                ),
            )


def discover_skills_sh(http: Http, out: dict[str, Candidate]) -> None:
    log("Searching skills.sh public search API…")
    seen_ids: set[str] = set()
    for q in SKILLS_SH_QUERIES:
        url = f"{SKILLS_SH_SEARCH}?q={urllib.parse.quote(q)}"
        status, body, _ = http.fetch(url, cache_ns="skills-sh")
        if status != 200:
            log(f"  skills.sh search {q!r} -> {status}")
            continue
        try:
            data = json.loads(body.decode("utf-8", "replace"))
        except json.JSONDecodeError:
            continue
        skills = data.get("skills") or []
        for s in skills:
            sid = s.get("id") or f"{s.get('source')}/{s.get('skillId')}"
            if not sid or sid in seen_ids:
                continue
            seen_ids.add(sid)
            source = s.get("source") or ""
            skill_id = s.get("skillId") or s.get("name") or ""
            if not source or "/" not in source:
                continue
            # skills.sh ids are owner/repo/skill; path is unknown until enrichment
            url = f"https://github.com/{source}"
            add_candidate(
                out,
                Candidate(
                    name=str(skill_id or s.get("name") or ""),
                    source_url=url,
                    repo=source,
                    skill_path="",
                    installs=int(s.get("installs") or 0),
                    discovery_source="skills.sh",
                    notes=f"skills.sh id={sid}",
                ),
            )
        time.sleep(0.05)
    log(f"  skills.sh unique skills: {len(seen_ids)}")


def discover_web_mentions(out: dict[str, Candidate]) -> None:
    for m in WEB_MENTIONS:
        add_candidate(
            out,
            Candidate(
                name=m["name"],
                source_url=m["url"],
                repo="",
                description="Official X (Twitter) agent skill documented at docs.x.com.",
                guessed_shelf="marketing",
                discovery_source=m["discovery_source"],
                notes=m["notes"],
                license="unknown",
                license_status="unknown",
            ),
        )


def soft_key(c: Candidate) -> str:
    return f"{(c.repo or '').lower()}::{slug(c.name)}"


def merge_by_name(items: list[Candidate]) -> list[Candidate]:
    """Fold skills.sh / list rows into the SKILL.md row when repo+name match."""
    with_path: dict[str, Candidate] = {}
    leftover: list[Candidate] = []
    for c in items:
        if c.repo and c.skill_path:
            k = soft_key(c)
            if k in with_path:
                add_candidate({with_path[k].key(): with_path[k]}, c)
                with_path[c.key() if False else k] = with_path[k]
            else:
                with_path[k] = c
        else:
            leftover.append(c)
    kept: dict[str, Candidate] = {c.key(): c for c in with_path.values()}
    for c in leftover:
        k = soft_key(c) if c.repo and c.name else ""
        if k and k in with_path:
            add_candidate({with_path[k].key(): with_path[k]}, c)
            # copy installs / sources onto the path-bearing row
            dest = with_path[k]
            if c.installs > dest.installs:
                dest.installs = c.installs
            if c.notes and c.notes not in (dest.notes or ""):
                dest.notes = (dest.notes + "; " if dest.notes else "") + c.notes
            parts: list[str] = []
            for s in (dest.discovery_source + "," + c.discovery_source).split(","):
                s = s.strip()
                if s and s not in parts:
                    parts.append(s)
            dest.discovery_source = ",".join(parts)
        else:
            kept[c.key()] = c
    return list(kept.values())


def enrich_candidates(http: Http, items: list[Candidate], catalog_names: set[str], max_frontmatter: int = 220, max_repos: int = 220) -> None:
    """Fill repo metadata, locate SKILL.md paths, and parse frontmatter for a cap of items."""
    items[:] = merge_by_name(items)
    log(f"Enriching {len(items)} candidates (frontmatter cap {max_frontmatter}, repo cap {max_repos})…")
    repo_cache: dict[str, dict[str, Any]] = {}
    paths_cache: dict[str, list[str]] = {}
    fm_used = 0

    def meta_for(repo: str) -> dict[str, Any]:
        if repo not in repo_cache:
            repo_cache[repo] = repo_meta(http, repo) if repo else {}
        return repo_cache[repo]

    # Score repos and only enrich a high-signal subset. Known collections already
    # have paths and metadata; the long tail of skills.sh hits is ranked by installs.
    repo_score: dict[str, float] = defaultdict(float)
    repo_has_path: set[str] = set()
    for c in items:
        if not c.repo:
            continue
        repo_score[c.repo] += math.log10(c.installs + 1) * 5 + math.log10(c.stars + 1) * 3 + 1
        if c.skill_path:
            repo_score[c.repo] += 50
            repo_has_path.add(c.repo)
        if "known-collection" in c.discovery_source:
            repo_score[c.repo] += 80
        org = c.repo.split("/")[0]
        if org in OFFICIAL_ORGS:
            repo_score[c.repo] += 40
    selected = set(repo_has_path)
    for repo, _ in sorted(repo_score.items(), key=lambda kv: kv[1], reverse=True):
        if len(selected) >= max_repos:
            break
        selected.add(repo)

    repos = sorted(selected)
    log(f"  fetching metadata for {len(repos)} of {len(repo_score)} repos")
    for i, repo in enumerate(repos, 1):
        if i % 25 == 0:
            log(f"  repo metadata {i}/{len(repos)}")
        meta_for(repo)

    # Expand repo-only candidates that have SKILL.md files (limit per repo)
    expanded: list[Candidate] = []
    seen_keys = set()
    for c in items:
        meta = meta_for(c.repo) if (c.repo and c.repo in selected) else (repo_cache.get(c.repo, {}) if c.repo else {})
        if meta:
            if not c.stars:
                c.stars = meta["stars"]
            if not c.last_commit:
                c.last_commit = meta["pushed_at"]
            if not c.default_branch:
                c.default_branch = meta["default_branch"]
            if (not c.license or c.license == "unknown") and meta.get("license_raw"):
                label, status = classify_license(meta["license_raw"])
                c.license, c.license_status = label, status
            if not c.description:
                c.description = meta.get("description") or ""
            c.repo = meta.get("repo") or c.repo
        # If we only have a repo and no skill path, try to find SKILL.md files
        if c.repo and not c.skill_path and c.repo in selected:
            if c.repo not in paths_cache:
                br = (meta or {}).get("default_branch") or "main"
                paths_cache[c.repo] = list_skill_md(http, c.repo, br)
            paths = paths_cache[c.repo]
            if paths:
                # Prefer a path whose folder matches the candidate name
                match = [p for p in paths if skill_name_from_path(p) == slug(c.name)]
                chosen = match or paths
                # If many skills, split into per-skill candidates (cap 12 per repo here)
                cap = 12 if c.discovery_source.startswith("awesome-list") or "github-repo-search" in c.discovery_source else 40
                for p in chosen[:cap]:
                    nc = Candidate(**{**asdict(c), "skill_path": p, "name": skill_name_from_path(p),
                                      "source_url": f"https://github.com/{c.repo}/blob/{(meta or {}).get('default_branch') or 'main'}/{p}"})
                    k = nc.key()
                    if k not in seen_keys:
                        seen_keys.add(k)
                        expanded.append(nc)
                continue
        k = c.key()
        if k not in seen_keys:
            seen_keys.add(k)
            expanded.append(c)

    # Prefer enriching high-signal rows first
    def pre_score(c: Candidate) -> float:
        s = math.log10(c.stars + 1) * 10 + math.log10(c.installs + 1) * 6
        if c.license_status.startswith("compatible"):
            s += 20
        if any(x in c.discovery_source for x in ("known-collection", "skills.sh")):
            s += 10
        if slug(c.name) in catalog_names or normalize_name(c.name) in catalog_names:
            s -= 30
        return s

    expanded.sort(key=pre_score, reverse=True)
    # Spread frontmatter across repos so one large catalog cannot consume the cap.
    per_repo_cap = 12
    per_repo_used: dict[str, int] = defaultdict(int)
    for c in expanded:
        if fm_used >= max_frontmatter:
            break
        if not c.repo or not c.skill_path:
            continue
        if per_repo_used[c.repo] >= per_repo_cap:
            continue
        br = c.default_branch or (meta_for(c.repo) or {}).get("default_branch") or "main"
        fm = fetch_skill_frontmatter(http, c.repo, br, c.skill_path)
        fm_used += 1
        per_repo_used[c.repo] += 1
        if fm.get("name"):
            c.name = slug(fm["name"]) or c.name
        if fm.get("description"):
            c.description = fm["description"].strip()
        if fm.get("license"):
            label, status = classify_license(fm["license"])
            # skill-level license wins when present
            c.license, c.license_status = label, status
        # rebuild URL with confirmed branch/path
        c.source_url = f"https://github.com/{c.repo}/blob/{br}/{c.skill_path}"
        if fm_used % 25 == 0:
            log(f"  frontmatter {fm_used}/{max_frontmatter}")

    items[:] = expanded
    log(f"  after path expansion: {len(items)} candidates; frontmatter fetched: {fm_used}")


def apply_catalog_and_shelves(
    items: list[Candidate],
    by_name: dict[str, dict[str, Any]],
    norm: dict[str, str],
) -> None:
    for c in items:
        if not c.guessed_shelf:
            shelf, conf = guess_shelf(c.name, c.description, c.skill_path)
            c.guessed_shelf, c.shelf_confidence = shelf, conf
        else:
            _, conf = guess_shelf(c.name, c.description, c.skill_path)
            c.shelf_confidence = max(c.shelf_confidence, conf)
        match = ""
        if c.name in by_name:
            match = c.name
        elif slug(c.name) in by_name:
            match = slug(c.name)
        elif normalize_name(c.name) in norm:
            match = norm[normalize_name(c.name)]
        if match:
            c.already_in_catalog = True
            c.catalog_match = match


def recency_points(iso: str) -> float:
    if not iso:
        return 0
    try:
        # handle Z
        t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except ValueError:
        return 0
    days = (datetime.now(timezone.utc) - t).days
    if days <= 30:
        return 16
    if days <= 90:
        return 12
    if days <= 180:
        return 8
    if days <= 365:
        return 4
    return 0


def rank(items: list[Candidate]) -> None:
    for c in items:
        score = 0.0
        if c.already_in_catalog:
            score -= 80
        if c.license_status == "compatible":
            score += 50
        elif c.license_status == "readme-only":
            score += 28
        elif c.license_status == "copyleft":
            score += 8
        elif c.license_status == "unknown":
            score += 10
        score += min(42.0, math.log10(c.stars + 1) * 10)
        score += min(24.0, math.log10(c.installs + 1) * 5)
        score += recency_points(c.last_commit)
        orgs = c.repo.split("/")[0] if c.repo else ""
        if orgs in OFFICIAL_ORGS:
            score += 22
        if "known-collection" in c.discovery_source:
            score += 8
        if "skills.sh" in c.discovery_source:
            score += 6
        if c.guessed_shelf in EMPTY_SHELVES:
            score += 16
        if c.description and len(c.description) >= 40:
            score += 6
        if c.skill_path.endswith("SKILL.md"):
            score += 8
        elif not c.skill_path:
            score -= 6
        # downrank huge bulk catalogs slightly (still useful as sources)
        if "alirezarezvani" in c.repo or "sickn33" in c.repo:
            score -= 8
        c.rank_score = round(score, 2)
    items.sort(key=lambda c: (c.rank_score, c.stars, c.installs), reverse=True)


def spot_check(http: Http, items: list[Candidate], n: int = 20) -> None:
    """Fetch a spread of candidate URLs to confirm they are real."""
    if not items:
        return
    picks: list[Candidate] = []
    # top 10 + some mid + some from empty shelves
    picks.extend(items[:10])
    if len(items) > 20:
        picks.extend(items[20:25])
    for shelf in EMPTY_SHELVES:
        for c in items:
            if c.guessed_shelf == shelf and c not in picks:
                picks.append(c)
                break
    # unique, cap
    seen = set()
    uniq = []
    for c in picks:
        if c.source_url in seen:
            continue
        seen.add(c.source_url)
        uniq.append(c)
        if len(uniq) >= n:
            break
    log(f"Spot-checking {len(uniq)} candidate URLs…")
    ok = 0
    for c in uniq:
        url = c.source_url
        # Prefer raw file when we have a blob URL
        check = url
        m = re.match(r"https://github.com/([^/]+)/([^/]+)/blob/([^/]+)/(.+)$", url)
        if m:
            check = f"{RAW_GH}/{m.group(1)}/{m.group(2)}/{m.group(3)}/{m.group(4)}"
        status, body, final = http.fetch(check, headers={"User-Agent": USER_AGENT, "Accept": "text/html,text/plain,*/*"}, cache_ns="spot")
        # treat cache hits and 200 as verified
        good = status in (200, 301, 302)
        if good and m and b"name:" not in body[:2000] and "name:" not in body.decode("utf-8", "replace")[:2000]:
            # still ok if page exists; SKILL.md should have name: in frontmatter
            text = body.decode("utf-8", "replace")[:4000]
            if "---" in text and re.search(r"^name\s*:", text, re.M):
                pass
            elif status == 200 and len(body) > 50:
                pass
            else:
                good = status == 200
        c.verified_url = f"HTTP {status} {final}"
        if good:
            ok += 1
            if c.notes:
                c.notes = c.notes + f"; spot-check HTTP {status}"
            else:
                c.notes = f"spot-check HTTP {status}"
        else:
            c.notes = (c.notes + "; " if c.notes else "") + f"UNREACHABLE HTTP {status}"
        log(f"  {status} {c.name} {check}")
    log(f"  spot-check passed {ok}/{len(uniq)}")


def write_csv(path: Path, items: list[Candidate]) -> None:
    fields = [
        "rank_score", "name", "source_url", "repo", "skill_path", "license",
        "license_status", "stars", "last_commit", "installs", "description",
        "guessed_shelf", "shelf_confidence", "already_in_catalog",
        "catalog_match", "discovery_source", "verified_url", "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for c in items:
            row = {k: getattr(c, k) for k in fields}
            w.writerow(row)


def md_escape(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def write_markdown(
    path: Path,
    items: list[Candidate],
    catalog_count: int,
    generated_at: str,
) -> None:
    new_items = [c for c in items if not c.already_in_catalog]
    compatible = [c for c in new_items if c.license_status in {"compatible", "readme-only"}]
    unknown = [c for c in new_items if c.license_status == "unknown"]
    copyleft = [c for c in new_items if c.license_status == "copyleft"]
    dupes = [c for c in items if c.already_in_catalog]
    by_shelf: dict[str, int] = defaultdict(int)
    for c in compatible:
        by_shelf[c.guessed_shelf or "unassigned"] += 1
    by_source: dict[str, int] = defaultdict(int)
    for c in items:
        for s in c.discovery_source.split(","):
            s = s.strip().split(":")[0]
            if s:
                by_source[s] += 1

    lines: list[str] = []
    a = lines.append
    a("# Agentpedia sourcing queue")
    a("")
    a(f"Generated **{generated_at}** (UTC) by `source_candidates.py`. Catalog compared against **{catalog_count}** existing Agentpedia names. This file does not modify the Agentpedia repo.")
    a("")
    a("## Counts")
    a("")
    a(f"- Unique candidates discovered: **{len(items)}**")
    a(f"- Already in the catalog (name match): **{len(dupes)}**")
    a(f"- New, license-compatible (MIT / Apache / BSD / ISC / CC-BY / CC0 or similar): **{len(compatible)}**")
    a(f"- New, license unknown (flag, do not copy until cleared): **{len(unknown)}**")
    a(f"- New, copyleft (link, do not relicense into Apache-2.0): **{len(copyleft)}**")
    a("")
    a("### New compatible candidates by guessed shelf")
    a("")
    a("| Shelf | Count |")
    a("| --- | ---: |")
    for shelf, n in sorted(by_shelf.items(), key=lambda kv: (-kv[1], kv[0])):
        flag = " (currently empty on Agentpedia)" if shelf in EMPTY_SHELVES else ""
        a(f"| {shelf}{flag} | {n} |")
    a("")
    a("### Discovery sources (a candidate can have more than one)")
    a("")
    for s, n in sorted(by_source.items(), key=lambda kv: (-kv[1], kv[0])):
        a(f"- {s}: {n}")
    a("")
    a("## Top 15 new compatible candidates")
    a("")
    a("| # | Name | Shelf | Stars | License | Source |")
    a("| ---: | --- | --- | ---: | --- | --- |")
    for i, c in enumerate(compatible[:15], 1):
        a(
            f"| {i} | `{md_escape(c.name)}` | {c.guessed_shelf} | {c.stars} | {md_escape(c.license)} | [{md_escape(c.repo or c.source_url)}]({c.source_url}) |"
        )
    a("")
    a("## Ranked queue (new compatible first, then unknown, then copyleft)")
    a("")
    a("Use this as the intake list. Prefer rows with a confirmed `SKILL.md` path, a compatible license, and a description.")
    a("")

    def table(rows: list[Candidate], heading: str, limit: int = 80) -> None:
        a(f"### {heading}")
        a("")
        a("| Rank | Name | Shelf | Stars | Installs (skills.sh) | License | Last push (repo) | Already listed | URL |")
        a("| ---: | --- | --- | ---: | ---: | --- | --- | --- | --- |")
        for c in rows[:limit]:
            last = (c.last_commit or "")[:10]
            a(
                f"| {c.rank_score} | `{md_escape(c.name)}` | {c.guessed_shelf} | {c.stars} | {c.installs or ''} | {md_escape(c.license)} | {last} | {'yes: ' + c.catalog_match if c.already_in_catalog else 'no'} | [source]({c.source_url}) |"
            )
        if len(rows) > limit:
            a("")
            a(f"_Plus {len(rows) - limit} more in `candidates.csv`._")
        a("")

    table(compatible, "New and license-compatible", 80)
    table(unknown, "New, license unknown (flag)", 40)
    table(copyleft, "New, copyleft (do not import text)", 20)
    table(dupes, "Name already in the Agentpedia catalog", 30)

    a("## Licensing and attribution rules")
    a("")
    a("- Agentpedia entries are published under Apache-2.0. Only import or adapt skills whose license allows that: MIT, Apache-2.0, BSD-2/3, ISC, 0BSD, Unlicense, CC0, CC-BY (keep attribution).")
    a("- Always keep the original copyright line, license name, and a `Source:` URL with the commit or tag you copied from.")
    a("- GPL, AGPL, and CC-BY-SA cannot be relicensed into Apache-2.0. Link to those repos from a brief original write-up; do not paste their SKILL.md.")
    a("- Unknown or README-only licenses (`readme-only`) need a LICENSE file or written permission before any text is copied. Until then, write an original Agentpedia skill on the same job, or skip.")
    a("- Do not copy trademarks, logos, or partner-audit badges. Descriptions may be shortened, but do not present someone else's skill as a first-party Agentpedia original.")
    a("")
    a("## Proposed faster pipeline")
    a("")
    a("1. Nightly (cloud agent or CI cron): run `source_candidates.py` against `main`'s `data/catalog.json` and commit `data/candidates.json` plus a short diff of new URLs. Do not hand-merge generated catalogs.")
    a("2. Raise the weekday drop from 1–3 hand-written entries to **5–10**, pulling the next unused compatible rows from the queue, preferring empty shelves (Education, Product, People) and official orgs.")
    a("3. Add `tools/new_entry.py import --from <github-blob-or-repo-url>` that fetches SKILL.md at a pinned commit, writes attribution into the entry (`Source`, license, copyright), maps a shelf, then runs skill-lint and the static audit.")
    a("4. Import is accepted only if lint scores 100, the audit is not On Hold (no critical / F), and the license is compatible. Otherwise leave the row in the queue with the failure reason.")
    a("5. Adapt, don't dump: tighten the skill to Agentpedia style, drop vendor telemetry, and keep scripts that are needed for the job. One skill per folder, one job per skill.")
    a("6. Inbound funnel: keep `/submit`, `/submit.md`, `/llms.txt`, and `tools/new_entry.py submit` for humans and agents. Route GitHub issue/PR templates into the same queue (`source: inbound`).")
    a("7. A weekly maintainer pass closes or rejects stale candidate rows (dead links, license still unknown after 30 days, duplicate of a dropped entry).")
    a("8. Optional: a public `Wanted` page on agentpedia.sh for the empty shelves, so inbound submissions aim at gaps instead of more git-commit helpers.")
    a("9. Attribution appears on the Book page and in NOTICE. Certificate and audit still start at Listed; a third-party skill does not inherit Verified just because the upstream repo is popular.")
    a("10. Until `import` ships, the daily-drop agent can use this CSV as its input list and open one PR per drop as today.")
    a("")
    a("## How to refresh")
    a("")
    a("```bash")
    a("python3 /workspace/agentpedia-sourcing/source_candidates.py \\")
    a("  --catalog /workspace/agentpedia/data/catalog.json \\")
    a("  --out /workspace/agentpedia-sourcing")
    a("```")
    a("")
    a("Delete `cache/` to force live refetches. The script uses `gh` when authenticated, otherwise the public GitHub API.")
    a("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_queue(raw_rows: list[dict], catalog_names: set[str], generated: str, out: Path, discovered: int) -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from sourcing.candidate_queue import build_document, load_queue, save_queue

    previous = load_queue(out).get("candidates") or []
    document = build_document(raw_rows, catalog_names, generated, previous, discovered=discovered)
    save_queue(out, document)
    counts = document["counts"]
    log(
        f"Wrote {out} ({counts['rows']} rows, {counts['compatible']} compatible, "
        f"{counts['readmeOnly']} readme-only, discovered {counts['discovered']})"
    )
    log(document["note"])
    if counts["compatible"] < 50 and counts["rows"] < 50:
        log("WARNING: fewer than 50 compatible rows in the queue.")
        return 1
    return 0


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    ap = argparse.ArgumentParser(description="Discover Agentpedia skill candidates and write data/candidates.json.")
    ap.add_argument("--catalog", type=Path, default=root / "data" / "catalog.json")
    ap.add_argument("--out", type=Path, default=root / "data" / "candidates.json", help="Queue file to write")
    ap.add_argument("--from-snapshot", type=Path, help="Compact an existing full snapshot instead of calling GitHub")
    ap.add_argument("--max-frontmatter", type=int, default=220)
    ap.add_argument("--max-repos", type=int, default=220)
    ap.add_argument("--skip-enrich", action="store_true")
    ap.add_argument("--report-dir", type=Path, help="Also write candidates.csv and candidates.md here")
    args = ap.parse_args()

    if not args.catalog.is_file():
        log(f"catalog not found: {args.catalog}")
        return 2
    by_name, norm, _shelves = load_catalog(args.catalog)
    names = set(by_name) | set(norm)
    log(f"Catalog: {len(by_name)} names from {args.catalog}")

    if args.from_snapshot:
        if not args.from_snapshot.is_file():
            log(f"snapshot not found: {args.from_snapshot}")
            return 2
        payload = json.loads(args.from_snapshot.read_text(encoding="utf-8"))
        raw_rows = payload.get("candidates") if isinstance(payload, dict) else payload
        if not isinstance(raw_rows, list):
            log("snapshot has no candidates list")
            return 2
        generated = payload.get("generatedAt") if isinstance(payload, dict) else now_iso()
        return _write_queue(raw_rows, names, generated or now_iso(), args.out, len(raw_rows))

    cache_root = root / "tools" / "sourcing" / "cache"
    cache = Cache(cache_root)
    http = Http(cache)
    bag: dict[str, Candidate] = {}
    discover_collections(http, bag)
    discover_skills_sh(http, bag)
    discover_topics_and_search(http, bag)
    discover_awesome_lists(http, bag)
    discover_web_mentions(bag)
    items = list(bag.values())
    log(f"Raw unique keys: {len(items)}")

    if not args.skip_enrich:
        enrich_candidates(http, items, names, max_frontmatter=args.max_frontmatter, max_repos=args.max_repos)

    apply_catalog_and_shelves(items, by_name, norm)
    rank(items)
    spot_check(http, [c for c in items if not c.already_in_catalog], n=18)

    generated = now_iso()
    if args.report_dir:
        args.report_dir.mkdir(parents=True, exist_ok=True)
        write_csv(args.report_dir / "candidates.csv", items)
        write_markdown(args.report_dir / "candidates.md", items, len(by_name), generated)
    raw_rows = [asdict(c) for c in items]
    return _write_queue(raw_rows, names, generated, args.out, len(items))


if __name__ == "__main__":
    raise SystemExit(main())
