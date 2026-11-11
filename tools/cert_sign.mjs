/**
 * Ed25519 signatures for Agentpedia certificates.
 *
 * The private key is AGENTPEDIA_SIGNING_KEY (PKCS#8 PEM). When it is unset
 * this script checks the canonical payload and leaves every record unsigned.
 */
import { createPrivateKey, createPublicKey, sign, verify } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const DATA_PATH = path.join(ROOT, "data", "certificates.json");
const PUBLIC_CERT_DIR = path.join(ROOT, "public", "cert");
const WELL_KNOWN_PATH = path.join(ROOT, "public", ".well-known", "agentpedia-signing-key.json");
const PINNED_KEY_PATH = path.join(ROOT, "certs", "public-key.json");

export function canonical(value) {
  if (value === null || typeof value === "boolean" || typeof value === "number" || typeof value === "string") {
    if (typeof value === "number" && !Number.isFinite(value)) {
      throw new Error("canonical JSON cannot represent a non-finite number");
    }
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map((item) => canonical(item)).join(",")}]`;
  }
  if (typeof value === "object") {
    const keys = Object.keys(value).sort();
    return `{${keys.map((key) => `${JSON.stringify(key)}:${canonical(value[key])}`).join(",")}}`;
  }
  throw new Error(`canonical JSON cannot represent ${typeof value}`);
}

export function normalizePem(raw) {
  const text = String(raw).trim().replace(/\\n/g, "\n");
  if (!text.includes("BEGIN PRIVATE KEY") && !text.includes("BEGIN PUBLIC KEY")) {
    throw new Error("AGENTPEDIA_SIGNING_KEY must be a PKCS#8 or SPKI PEM block");
  }
  return text.endsWith("\n") ? text : `${text}\n`;
}

export function pemBody(pem) {
  return String(pem).replace(/-----[^-]+-----/g, "").replace(/\s+/g, "");
}

export function signCanonical(canonicalText, privatePem) {
  const key = createPrivateKey(normalizePem(privatePem));
  const signature = sign(null, Buffer.from(canonicalText, "utf8"), key);
  const publicKeyPem = createPublicKey(key).export({ type: "spki", format: "pem" });
  return {
    signature: signature.toString("base64"),
    publicKeyPem: String(publicKeyPem),
  };
}

export function verifyCanonical(canonicalText, signatureB64, publicKeyPem) {
  return verify(
    null,
    Buffer.from(canonicalText, "utf8"),
    createPublicKey(normalizePem(publicKeyPem)),
    Buffer.from(signatureB64, "base64"),
  );
}

function readJson(file) {
  return JSON.parse(readFileSync(file, "utf8"));
}

function writeJson(file, value) {
  writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}

function assertCanonical(document) {
  const again = canonical(document.payload);
  if (again !== document.canonical) {
    throw new Error(`canonical payload mismatch for ${document.payload?.id ?? "a certificate"}`);
  }
}

function signDocument(document, privatePem, kid) {
  assertCanonical(document);
  const signed = signCanonical(document.canonical, privatePem);
  document.signed = true;
  document.signature = { alg: "Ed25519", kid, value: signed.signature };
  return signed.publicKeyPem;
}

export function signCatalog(privatePem) {
  const catalog = readJson(DATA_PATH);
  const pinned = exists(PINNED_KEY_PATH) ? readJson(PINNED_KEY_PATH) : null;
  const kid = pinned?.kid || "primary";
  let publicKeyPem = "";
  for (const document of catalog.certificates) {
    publicKeyPem = signDocument(document, privatePem, kid);
    const publicPath = path.join(PUBLIC_CERT_DIR, `${document.payload.id}.json`);
    writeJson(publicPath, document);
  }
  if (pinned?.publicKeyPem && pemBody(pinned.publicKeyPem) !== pemBody(publicKeyPem)) {
    throw new Error("AGENTPEDIA_SIGNING_KEY does not match certs/public-key.json");
  }
  catalog.signing = { alg: "Ed25519", signed: true };
  writeJson(DATA_PATH, catalog);
  const wellKnown = exists(WELL_KNOWN_PATH) ? readJson(WELL_KNOWN_PATH) : { schema: "agentpedia.signing-key.v1", keys: [] };
  wellKnown.configured = true;
  wellKnown.pinned = Boolean(pinned?.publicKeyPem);
  wellKnown.alg = "Ed25519";
  wellKnown.keys = [{ kid, alg: "Ed25519", publicKeyPem }];
  wellKnown.note = "This build signed every certificate with AGENTPEDIA_SIGNING_KEY.";
  writeJson(WELL_KNOWN_PATH, wellKnown);
  return catalog.certificates.length;
}

function exists(file) {
  try {
    readFileSync(file);
    return true;
  } catch {
    return false;
  }
}

function checkCanonicalFiles() {
  if (!exists(DATA_PATH)) {
    throw new Error("data/certificates.json is missing. Run tools/build_index.py first.");
  }
  const catalog = readJson(DATA_PATH);
  for (const document of catalog.certificates) assertCanonical(document);
  return catalog.certificates.length;
}

function main() {
  const count = checkCanonicalFiles();
  const privatePem = process.env.AGENTPEDIA_SIGNING_KEY;
  if (!privatePem || !privatePem.trim()) {
    console.log(`AGENTPEDIA_SIGNING_KEY is unset. ${count} certificate(s) stay unsigned.`);
    return;
  }
  const signed = signCatalog(privatePem);
  console.log(`signed ${signed} certificate(s) with Ed25519`);
}

const isMain = process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href;
if (isMain) {
  try {
    main();
  } catch (error) {
    console.error(`error: ${error.message}`);
    process.exit(1);
  }
}
