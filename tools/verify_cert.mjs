/**
 * Verify one Agentpedia certificate.
 *
 *   node tools/verify_cert.mjs public/cert/skill-csv-profile.json
 *   node tools/verify_cert.mjs https://agentpedia-ten.vercel.app/cert/skill-csv-profile.json
 *
 * Exit 0 when the Ed25519 signature matches the pinned public key.
 * Exit 2 when the record is explicitly unsigned.
 * Exit 1 when the signature is missing, forged, or the canonical payload was edited.
 */
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { canonical, verifyCanonical } from "./cert_sign.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");

function arg(name) {
  const index = process.argv.indexOf(name);
  if (index === -1) return "";
  return process.argv[index + 1] || "";
}

async function readTarget(target) {
  if (target.startsWith("http://") || target.startsWith("https://")) {
    const response = await fetch(target);
    if (!response.ok) throw new Error(`fetch ${target} failed: ${response.status}`);
    return { document: await response.json(), url: target };
  }
  const file = path.resolve(target);
  return { document: JSON.parse(readFileSync(file, "utf8")), url: "" };
}

function keyFromDocument(document) {
  const key = document.keys?.[0]?.publicKeyPem || document.publicKeyPem;
  if (!key) throw new Error("signing key file has no publicKeyPem");
  return key;
}

async function loadKey(targetUrl) {
  const explicit = arg("--key");
  if (explicit) {
    if (explicit.startsWith("http://") || explicit.startsWith("https://")) {
      const response = await fetch(explicit);
      if (!response.ok) throw new Error(`fetch ${explicit} failed: ${response.status}`);
      const body = await response.text();
      if (explicit.endsWith(".json") || body.trim().startsWith("{")) return keyFromDocument(JSON.parse(body));
      return body;
    }
    const body = readFileSync(path.resolve(explicit), "utf8");
    if (explicit.endsWith(".json") || body.trim().startsWith("{")) return keyFromDocument(JSON.parse(body));
    return body;
  }
  if (targetUrl) {
    const origin = new URL(targetUrl).origin;
    const keyUrl = new URL("/.well-known/agentpedia-signing-key.json", origin);
    const response = await fetch(keyUrl);
    if (!response.ok) throw new Error(`fetch ${keyUrl} failed: ${response.status}`);
    return keyFromDocument(await response.json());
  }
  const pinned = path.join(ROOT, "certs", "public-key.json");
  const wellKnown = path.join(ROOT, "public", ".well-known", "agentpedia-signing-key.json");
  try {
    return keyFromDocument(JSON.parse(readFileSync(pinned, "utf8")));
  } catch {
    return keyFromDocument(JSON.parse(readFileSync(wellKnown, "utf8")));
  }
}

async function main() {
  const target = process.argv.slice(2).find((item) => !item.startsWith("--") && process.argv[process.argv.indexOf(item) - 1] !== "--key");
  if (!target) {
    throw new Error("pass a certificate JSON file or URL");
  }
  const { document, url } = await readTarget(target);
  const again = canonical(document.payload);
  if (again !== document.canonical) {
    throw new Error("canonical payload does not match the payload object");
  }
  if (!document.signed || !document.signature?.value) {
    console.log(`${document.payload.id} is unsigned. Nothing was forged; no key signed this build.`);
    process.exitCode = 2;
    return;
  }
  const key = await loadKey(url);
  const ok = verifyCanonical(document.canonical, document.signature.value, key);
  if (!ok) throw new Error("signature does not match the public key");
  console.log(`${document.payload.id} signature matches (${document.signature.alg}, ${document.signature.kid}).`);
  console.log(`status ${document.payload.status}, tier ${document.payload.displayTier}, commit ${document.payload.sourceCommit}`);
}

main().catch((error) => {
  console.error(`error: ${error.message}`);
  process.exit(1);
});
