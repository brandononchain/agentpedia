# Certificates

`records/<id>.json` is the claim: tier, source commit, content digest, issue date, and an optional human review.

`checks/<id>.json` is the manifest `tools/verify_checks.py` runs. Checks live outside the skill folder so they do not change the entry digest.

`results/<id>.json` is a harness result. Commit one only after the harness writes it. Do not hand-edit `ok` or the stdout.

The catalog build issues a Listed record for every skill with a skill-lint score of 100, and for every agent whose bundled skills all score 100. It refuses a Verified or Certified claim that lacks a matching passing result. Certified also requires `review.reviewer`, `review.date`, and `review.notes`.

## Signing

```bash
node tools/gen_signing_key.mjs
```

That writes `agentpedia-signing-key.pem` (mode 600, gitignored) and `certs/public-key.json`. Commit the public JSON only.

Set `AGENTPEDIA_SIGNING_KEY` to the PEM contents:

- Vercel project, Production and Preview
- GitHub Actions secret, if a workflow should sign

`npm run build` runs `tools/cert_sign.mjs` after the catalog. With the secret set, every `/cert/<id>.json` gets an Ed25519 signature over the canonical payload. Without it, `signed` is false and `signature` is null. The build fails if the secret’s public key does not match `certs/public-key.json`.

Verify:

```bash
node tools/verify_cert.mjs https://agentpedia.sh/cert/skill-csv-profile.json
```

Exit 0 matches. Exit 2 means unsigned. Exit 1 means the signature does not match.

The public key is served at `https://agentpedia.sh/.well-known/agentpedia-signing-key.json`. That origin comes from `config/site.json`.
