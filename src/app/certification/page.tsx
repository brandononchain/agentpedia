import type { Metadata } from "next";
import Link from "next/link";
import { ArticleFrame } from "@/components/article-frame";
import { Contents } from "@/components/contents";
import { certificates } from "@/lib/certificates";
import { FaqList } from "@/components/faq-list";
import { JsonLd } from "@/components/json-ld";
import { CERT_FAQ, faqNode } from "@/lib/seo";
import { SITE_NAME, siteMeta } from "@/lib/site";

export const metadata: Metadata = siteMeta("/certification", {
  title: "Certification",
  description: `What ${SITE_NAME} Listed, Verified, and Certified certificates check, and what they do not guarantee.`,
  keywords: ["Listed", "Verified", "Certified", "agent skills", SITE_NAME],
});

export default function CertificationPage() {
  const { stats } = certificates;
  const example = certificates.certificates.find((item) => item.payload.id === "skill-csv-profile");
  return (
    <ArticleFrame
      title="Certification"
      lede={`${SITE_NAME} publishes a certificate for every skill and agent that passes the lint gate. The certificate names a tier, one source commit, and a date. It is a public record of those checks. It is not a security audit.`}
      path="/certification"
      crumbs={[
        { href: "/", label: "Home" },
        { label: "Certification" },
      ]}
    >
      <Contents
        items={[
          { id: "tiers", text: "Tiers", depth: 2 },
          { id: "listed", text: "Listed", depth: 2 },
          { id: "verified", text: "Verified", depth: 2 },
          { id: "certified", text: "Certified", depth: 2 },
          { id: "status", text: "Status", depth: 2 },
          { id: "signing", text: "Signing", depth: 2 },
          { id: "counts", text: "This build", depth: 2 },
          { id: "faq", text: "Questions", depth: 2 },
        ]}
      />
      <div className="wiki-prose">
        <section id="tiers">
          <h2>Tiers</h2>
          <p>
            A higher tier includes the checks below it. A badge shows the tier that is current today. When the files
            change, or a date passes, the badge says re-check pending or expired instead of the claimed tier.
          </p>
        </section>
        <section id="listed">
          <h3>Listed</h3>
          <p>
            A skill is Listed when skill-lint scores 100. The score starts at 100. An error subtracts 25, a warning
            subtracts 8, and an info finding subtracts 2, so 100 means zero of each. That is the same gate the directory
            already uses. The rule list is <Link href="/lint">How we lint</Link>.
          </p>
          <p>
            An agent is Listed when its manifest is accepted and every bundled skill scores 100. Agents are not passed
            through skill-lint. <code>AGENT.md</code> is not a <code>SKILL.md</code>.
          </p>
          <p>
            Listed does not install the entry and does not run it. It does not review the advice in the article. It
            expires 365 days after the issue date, and earlier if the entry&apos;s file digest changes.
          </p>
        </section>
        <section id="verified">
          <h3>Verified</h3>
          <p>
            Verified is Listed plus a recorded run of <code>tools/verify_checks.py</code>. The harness copies the entry
            to a temporary directory and checks that <code>SKILL.md</code> or <code>AGENT.md</code> is non-empty. It
            then runs each declared eval as a subprocess: no shell, a timeout, and an environment limited to{" "}
            <code>PATH</code>, locale, and Python isolation flags. Home and temp point at a fresh directory. Secrets
            from the parent process are dropped.
          </p>
          <p>
            The result file lives in <code>certs/results/</code>. The build refuses a Verified or Certified claim that
            has no passing result, or whose result digest and commit do not match the certificate record. This volume
            does not invent those results.
          </p>
          <p>
            Verified does not scan the entry for malware. The sandbox is a scrubbed subprocess, not a virtual machine.
            A passing eval shows that the declared command printed what the manifest required. It does not show that
            every other command the skill describes is correct. A run stays current for 90 days. Editing the entry, the
            harness, or the check manifest sets the certificate to re-check pending.
          </p>
        </section>
        <section id="certified">
          <h3>Certified</h3>
          <p>
            Certified is a current Verified run plus a human review stored in the certificate record: a GitHub login, a
            date, and notes. There is no Certified entry in this repository until a person writes that review. The
            publisher does not fill one in.
          </p>
          <p>
            A review is a reading of the entry and the recorded run. It is not a security audit unless the notes say
            that, and these notes do not. Certified expires on the earlier of the 90-day run window and 365 days after
            the review date.
          </p>
        </section>
        <section id="status">
          <h2>Status</h2>
          <p>
            Active means the claim still matches the files and the dates. Re-check pending means the entry digest, the
            harness, or the declared checks changed after the record was written. Expired means a revalidation date has
            passed. Withheld means the lint score is no longer 100. Re-check pending takes priority over expiry: a
            changed tree is pending even when the old date would also have expired.
          </p>
          <p>{certificates.certificates[0]?.payload.revalidation.sourceRule}</p>
          <p>{certificates.certificates[0]?.payload.revalidation.expiryRule}</p>
        </section>
        <section id="signing">
          <h2>Signing</h2>
          <p>
            Each certificate JSON carries a canonical payload: object keys sorted, no insignificant whitespace, UTF-8.
            When <code>AGENTPEDIA_SIGNING_KEY</code> is set at build time, <code>tools/cert_sign.mjs</code> signs those
            bytes with Ed25519 and writes the signature beside the payload. The private key is a PKCS#8 PEM. It is not
            in this repository. <code>*.pem</code> is gitignored.
          </p>
          <p>
            {certificates.signing.signed
              ? "This build signed the records."
              : "This build left every record unsigned. The signature field is null, and signed is false. That is the honest state until a key is configured."}{" "}
            The public key, when one is pinned, is published at{" "}
            <a href={example?.payload.urls.publicKey ?? "/.well-known/agentpedia-signing-key.json"}>
              {example?.payload.urls.publicKey ?? "/.well-known/agentpedia-signing-key.json"}
            </a>
            .
          </p>
          <p>To verify one record:</p>
          <pre className="snippet">
            <code>{`node tools/verify_cert.mjs ${example?.payload.urls.record ?? "/cert/skill-csv-profile.json"}`}</code>
          </pre>
          <p>
            Exit 0 means the signature matches. Exit 2 means the record is unsigned. Exit 1 means the signature is
            missing or does not match.
          </p>
          <p>To start signing production builds:</p>
          <ol>
            <li>
              Run <code>node tools/gen_signing_key.mjs</code>. That writes a PEM with mode 600 and{" "}
              <code>certs/public-key.json</code>. Commit only the public JSON.
            </li>
            <li>
              Set <code>AGENTPEDIA_SIGNING_KEY</code> to the PEM contents on Vercel, for Production and Preview, and as
              a GitHub Actions secret if a workflow should sign.
            </li>
            <li>Redeploy. The build fails if the secret&apos;s public key does not match the pinned file.</li>
            <li>
              Confirm with the verify command above. Until that secret exists, badges and pages still publish, and they
              say the record is unsigned.
            </li>
          </ol>
        </section>
        <section id="counts">
          <h2>This build</h2>
          <p>
            {stats.total} certificates. {stats.listed} listed, {stats.verified} verified, {stats.certified} certified.
            {stats.recheckPending ? ` ${stats.recheckPending} re-check pending.` : ""}
            {stats.expired ? ` ${stats.expired} expired.` : ""}
            {stats.withheld ? ` ${stats.withheld} withheld.` : ""} Founders add an entry through{" "}
            <Link href="/certify">the submission path</Link>.
          </p>
        </section>
        <section id="faq">
          <h2>Questions</h2>
          <FaqList items={CERT_FAQ} />
        </section>
      </div>
      <JsonLd data={{ "@context": "https://schema.org", ...faqNode(CERT_FAQ) }} />
    </ArticleFrame>
  );
}
