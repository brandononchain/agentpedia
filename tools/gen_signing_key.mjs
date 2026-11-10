/**
 * Generate the Ed25519 key Agentpedia uses to sign certificates.
 *
 * The private key is written to a PEM file and must stay out of git.
 * Commit only the public key JSON, then store the PEM as
 * AGENTPEDIA_SIGNING_KEY in Vercel and GitHub Actions.
 */
import { generateKeyPairSync } from "node:crypto";
import { writeFileSync } from "node:fs";
import path from "node:path";

function arg(name, fallback) {
  const index = process.argv.indexOf(name);
  if (index === -1) return fallback;
  const value = process.argv[index + 1];
  if (!value || value.startsWith("--")) {
    throw new Error(`${name} needs a path`);
  }
  return value;
}

const out = path.resolve(arg("--out", "agentpedia-signing-key.pem"));
const publicPath = path.resolve(arg("--public", "certs/public-key.json"));
const { publicKey, privateKey } = generateKeyPairSync("ed25519");
const privatePem = privateKey.export({ type: "pkcs8", format: "pem" });
const publicPem = publicKey.export({ type: "spki", format: "pem" });

writeFileSync(out, String(privatePem), { mode: 0o600, flag: "wx" });
writeFileSync(
  publicPath,
  `${JSON.stringify({ kid: "primary", alg: "Ed25519", publicKeyPem: String(publicPem) }, null, 2)}\n`,
  { flag: "wx" },
);

console.log(`Wrote the private key to ${out}`);
console.log(`Wrote the public key to ${publicPath}`);
console.log("Commit the public key. Do not commit the PEM.");
console.log("Set AGENTPEDIA_SIGNING_KEY to the PEM contents in Vercel and in GitHub Actions, then redeploy.");
