#!/usr/bin/env python3
"""Generate an Ed25519 keypair for Agentpedia certificates.

The private key is a base64-encoded 32-byte seed. It is written to a file
and is never printed. Commit only the public JSON.

    python3 tools/signing_keygen.py --out agentpedia-signing-key.txt --public certs/public-key.json
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

NODE = r"""
import { generateKeyPairSync } from "node:crypto";
import { writeFileSync } from "node:fs";

const out = process.argv[1];
const { privateKey, publicKey } = generateKeyPairSync("ed25519");
const der = privateKey.export({ type: "pkcs8", format: "der" });
const seed = Buffer.from(der).subarray(der.length - 32).toString("base64");
const publicPem = String(publicKey.export({ type: "spki", format: "pem" }));
const publicDer = publicKey.export({ type: "spki", format: "der" });
const publicRaw = Buffer.from(publicDer).subarray(publicDer.length - 32).toString("base64");
writeFileSync(out, seed + "\n", { mode: 0o600 });
process.stdout.write(JSON.stringify({ publicKeyPem: publicPem, publicKey: publicRaw }));
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Write an Ed25519 signing key. The private key is not printed.")
    parser.add_argument("--out", default="agentpedia-signing-key.txt", help="Private key file. Refuses to overwrite.")
    parser.add_argument("--public", default="certs/public-key.json", help="Public key JSON. Refuses to overwrite.")
    parser.add_argument("--kid", default="primary")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    private_path = Path(args.out).resolve()
    public_path = Path(args.public).resolve()
    if private_path.exists():
        raise SystemExit(f"refusing to overwrite {private_path}")
    if public_path.exists():
        raise SystemExit(f"refusing to overwrite {public_path}")
    public_path.parent.mkdir(parents=True, exist_ok=True)
    completed = subprocess.run(
        ["node", "--input-type=module", "-e", NODE, str(private_path)],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        private_path.unlink(missing_ok=True)
        sys.stderr.write(completed.stderr)
        raise SystemExit(completed.returncode or 1)
    try:
        public = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        private_path.unlink(missing_ok=True)
        raise SystemExit("key generation did not return a public key") from exc
    os.chmod(private_path, stat.S_IRUSR | stat.S_IWUSR)
    document = {
        "kid": args.kid,
        "alg": "Ed25519",
        "publicKey": public["publicKey"],
        "publicKeyPem": public["publicKeyPem"],
    }
    public_path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote the private key to {private_path}")
    print(f"Wrote the public key to {public_path}")
    print("Commit the public key only. Set AGENTPEDIA_SIGNING_KEY to the private file contents.")
    print("The private key was not printed.")


if __name__ == "__main__":
    main()
