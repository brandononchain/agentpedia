# Certificates

`records/<id>.json` is the claim: tier, source commit, content digest, issue date, and an optional human review.

`checks/<id>.json` is the manifest `tools/verify_checks.py` runs. Checks live outside the skill folder so they do not change the entry digest.

The digest hashes the entry directory. It covers the instructions and the assets. Two catalog fields in the frontmatter are left out before hashing: `category` and `subshelf`, on a skill's `metadata` block or at the top of an agent manifest. The shelf number, the order of sub-shelves, and the call number live in `skills/<shelf>/category.json`, which is outside the entry directory, so a reorder does not change the digest. Editing a step, a script, a reference, or any other file still does.

`results/<id>.json` is a harness result. Commit one only after the harness writes it. Do not hand-edit `ok` or the stdout.

The catalog build issues a Listed record for every skill with a skill-lint score of 100, and for every agent whose bundled skills all score 100, including an entry the static audit puts on hold so the badge can say so. Listing still requires the audit status to be anything but on hold. A Listed record is updated to the current digest when that gate still passes. Verified and Certified go re-check pending when the digest changes. The build refuses a Verified or Certified claim that lacks a matching passing result. Certified also requires `review.reviewer`, `review.date`, and `review.notes`, and the reviewer cannot be the recorded author.

## Signing

```bash
python3 tools/signing_keygen.py
```

That writes `agentpedia-signing-key.txt` (mode 600, gitignored) and `certs/public-key.json`. The private file is a base64 32-byte seed. The command prints the paths and does not print the key. Commit the public JSON only. `node tools/gen_signing_key.mjs` still writes a PEM if you prefer that form.

Set `AGENTPEDIA_SIGNING_KEY` to the base64 seed or the PEM contents:

- Vercel project, Production and Preview
- GitHub Actions secret, if a workflow should sign

`npm run build` runs `tools/cert_sign.mjs` after the catalog. With the secret set, every `/cert/<id>.json` gets an Ed25519 signature over the canonical payload. Without it, `signed` is false and `signature` is null. The build fails if the secret’s public key does not match `certs/public-key.json`.

Verify:

```bash
python3 tools/verify_certificate.py https://agentpedia.sh/cert/skill-csv-profile.json
```

Exit 0 matches. Exit 2 means unsigned. Exit 1 means the signature does not match.

The public key is served at `https://agentpedia.sh/.well-known/agentpedia-signing-key.json`. That origin comes from `config/site.json`.
