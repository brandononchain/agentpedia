#!/usr/bin/env python3
"""Verify one Agentpedia certificate.

    python3 tools/verify_certificate.py public/cert/skill-csv-profile.json
    python3 tools/verify_certificate.py https://agentpedia.sh/cert/skill-csv-profile.json

Exit 0 when the Ed25519 signature matches the public key.
Exit 2 when the record is explicitly unsigned.
Exit 1 when the signature is missing, forged, or the canonical payload was edited.

The public key is read from --key, from /.well-known/agentpedia-signing-key.json
on the same origin as an https URL, or from certs/public-key.json.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from certlib import canonical  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify an Agentpedia certificate signature.")
    parser.add_argument("target", help="Certificate JSON file or https URL")
    parser.add_argument("--key", default="", help="Public key JSON, PEM file, or URL")
    return parser.parse_args()


def read_target(target: str) -> tuple[dict, str]:
    if target.startswith("http://") or target.startswith("https://"):
        with urllib.request.urlopen(target, timeout=30) as response:
            return json.load(response), target
    return json.loads(Path(target).read_text(encoding="utf-8")), ""


def key_material(document: dict | str) -> str:
    if isinstance(document, str):
        return document
    keys = document.get("keys") or []
    if keys:
        return str(keys[0].get("publicKeyPem") or keys[0].get("publicKey") or "")
    return str(document.get("publicKeyPem") or document.get("publicKey") or "")


def load_key(explicit: str, target_url: str) -> str:
    if explicit:
        if explicit.startswith("http://") or explicit.startswith("https://"):
            with urllib.request.urlopen(explicit, timeout=30) as response:
                body = response.read().decode("utf-8")
        else:
            body = Path(explicit).read_text(encoding="utf-8")
        if body.lstrip().startswith("{"):
            return key_material(json.loads(body))
        return body
    if target_url:
        base = "/".join(target_url.split("/")[:3])
        with urllib.request.urlopen(f"{base}/.well-known/agentpedia-signing-key.json", timeout=30) as response:
            return key_material(json.load(response))
    for path in (ROOT / "certs" / "public-key.json", ROOT / "public" / ".well-known" / "agentpedia-signing-key.json"):
        if path.is_file():
            return key_material(json.loads(path.read_text(encoding="utf-8")))
    raise SystemExit("no public key. Pass --key or pin certs/public-key.json")


def verify(canonical_text: str, signature: str, public_key: str) -> bool:
    import subprocess

    script = """
import { verifyCanonical } from "./tools/cert_sign.mjs";
const chunks = [];
for await (const chunk of process.stdin) chunks.push(chunk);
const payload = JSON.parse(Buffer.concat(chunks).toString("utf8"));
const ok = verifyCanonical(payload.canonical, payload.signature, payload.publicKey);
process.exit(ok ? 0 : 1);
"""
    completed = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT,
        input=json.dumps({"canonical": canonical_text, "signature": signature, "publicKey": public_key}),
        text=True,
        capture_output=True,
    )
    if completed.returncode not in {0, 1}:
        sys.stderr.write(completed.stderr)
        raise SystemExit(completed.returncode or 1)
    return completed.returncode == 0


def main() -> None:
    args = parse_args()
    document, url = read_target(args.target)
    payload = document.get("payload")
    if not isinstance(payload, dict):
        raise SystemExit("certificate has no payload")
    again = canonical(payload)
    if again != document.get("canonical"):
        raise SystemExit("canonical payload does not match the payload object")
    identifier = payload.get("id") or "certificate"
    signature = (document.get("signature") or {}) if isinstance(document.get("signature"), dict) else {}
    if not document.get("signed") or not signature.get("value"):
        print(f"{identifier} is unsigned. Nothing was forged; no key signed this build.")
        raise SystemExit(2)
    public_key = load_key(args.key, url)
    if not public_key:
        raise SystemExit("public key material is empty")
    if not verify(again, str(signature["value"]), public_key):
        raise SystemExit("signature does not match the public key")
    kid = signature.get("kid") or "unknown"
    print(f"{identifier} signature matches (Ed25519, {kid}).")
    print(f"status {payload.get('status')}, tier {payload.get('displayTier')}, commit {payload.get('sourceCommit')}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 — CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
