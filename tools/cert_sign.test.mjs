import assert from "node:assert/strict";
import { generateKeyPairSync } from "node:crypto";
import test from "node:test";
import { canonical, signCanonical, verifyCanonical } from "./cert_sign.mjs";

test("canonical JSON matches the sorted compact form", () => {
  assert.equal(canonical({ b: 1, a: { d: true, c: ["x", null] } }), '{"a":{"c":["x",null],"d":true},"b":1}');
});

test("an Ed25519 signature verifies and a flipped byte does not", () => {
  const { privateKey, publicKey } = generateKeyPairSync("ed25519");
  const privatePem = privateKey.export({ type: "pkcs8", format: "pem" });
  const publicPem = publicKey.export({ type: "spki", format: "pem" });
  const text = canonical({ id: "skill-csv-profile", status: "active" });
  const signed = signCanonical(text, privatePem);
  assert.equal(verifyCanonical(text, signed.signature, publicPem), true);
  assert.equal(verifyCanonical(text + " ", signed.signature, publicPem), false);
});
