#!/usr/bin/env python3
"""Create, revoke, and list Agentpedia Brain API keys.

Keys look like ap_live_ plus 32 letters or digits. Redis stores only
sha256(key). Requires UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN.
When those are unset the server runs keyless with an in-memory limiter;
this script refuses to invent a key it cannot store.

    python3 tools/brain_key.py create --org acme --plan free
    python3 tools/brain_key.py list
    python3 tools/brain_key.py revoke ap_live_...
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import string
import sys
import urllib.request
from datetime import datetime, timezone

PLANS = ("free", "builder", "team", "enterprise")
ALPHABET = string.ascii_letters + string.digits


def redis_env() -> tuple[str, str]:
    url = os.environ.get("UPSTASH_REDIS_REST_URL", "").strip().rstrip("/")
    token = os.environ.get("UPSTASH_REDIS_REST_TOKEN", "").strip()
    if not url or not token:
        raise SystemExit(
            "UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN are unset. "
            "The Brain runs keyless with an in-memory limiter until Redis is configured."
        )
    return url, token


def command(url: str, token: str, *args: str):
    request = urllib.request.Request(
        url,
        data=json.dumps(list(args)).encode("utf-8"),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = json.load(response)
    if isinstance(body, dict) and body.get("error"):
        raise SystemExit(str(body["error"]))
    if isinstance(body, dict) and "result" in body:
        return body["result"]
    return body


def key_hash(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def redis_key(digest: str) -> str:
    return f"brain:key:{digest}"


def new_key() -> str:
    return "ap_live_" + "".join(secrets.choice(ALPHABET) for _ in range(32))


def create(args: argparse.Namespace) -> None:
    if args.plan not in PLANS:
        raise SystemExit(f"plan must be one of {', '.join(PLANS)}")
    url, token = redis_env()
    raw = new_key()
    digest = key_hash(raw)
    record = {
        "org": args.org,
        "plan": args.plan,
        "created": datetime.now(timezone.utc).isoformat(),
        "last_used": None,
        "scopes": [part.strip() for part in args.scopes.split(",") if part.strip()] or ["read"],
    }
    if args.monthly_limit:
        record["monthlyLimit"] = args.monthly_limit
    command(url, token, "SET", redis_key(digest), json.dumps(record))
    command(url, token, "SADD", "brain:keys", digest)
    print(raw)
    print("Store this key now. It will not be shown again.")
    print(f"org: {args.org}")
    print(f"plan: {args.plan}")
    print(f"id: {digest[:12]}")


def revoke(args: argparse.Namespace) -> None:
    url, token = redis_env()
    raw = args.key
    digest = raw if len(raw) == 64 and all(char in "0123456789abcdef" for char in raw) else key_hash(raw)
    current = command(url, token, "GET", redis_key(digest))
    if not current:
        raise SystemExit("no key with that id")
    record = json.loads(current) if isinstance(current, str) else current
    record["revoked"] = True
    command(url, token, "SET", redis_key(digest), json.dumps(record))
    print(f"revoked {digest[:12]}")


def list_keys(_args: argparse.Namespace) -> None:
    url, token = redis_env()
    members = command(url, token, "SMEMBERS", "brain:keys") or []
    if not members:
        print("no keys")
        return
    for digest in sorted(str(item) for item in members):
        current = command(url, token, "GET", redis_key(digest))
        if not current:
            print(f"{digest[:12]}  missing")
            continue
        record = json.loads(current) if isinstance(current, str) else current
        state = "revoked" if record.get("revoked") else "active"
        print(
            f"{digest[:12]}  {state}  org={record.get('org')}  plan={record.get('plan')}  "
            f"created={record.get('created')}  last_used={record.get('last_used')}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage Agentpedia Brain API keys in Upstash Redis.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    created = sub.add_parser("create")
    created.add_argument("--org", required=True)
    created.add_argument("--plan", required=True, choices=PLANS)
    created.add_argument("--scopes", default="read")
    created.add_argument("--monthly-limit", type=int, default=0)
    created.set_defaults(func=create)
    revoked = sub.add_parser("revoke")
    revoked.add_argument("key", help="The ap_live_ key, or its sha256 hex id")
    revoked.set_defaults(func=revoke)
    listed = sub.add_parser("list")
    listed.set_defaults(func=list_keys)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
