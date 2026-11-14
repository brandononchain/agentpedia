import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArticleFrame } from "@/components/article-frame";
import { Contents } from "@/components/contents";
import { CopyButton } from "@/components/copy-button";
import { badgeAlt, certificateById, certificates, embedHtml, embedMarkdown, tierLabel } from "@/lib/certificates";
import { metaDescription } from "@/lib/seo";
import { absoluteUrl, REPO_URL, SITE_NAME, siteMeta } from "@/lib/site";
import { formatDropDate } from "@/lib/format";

type Params = { id: string };

export const dynamicParams = false;

export function generateStaticParams() {
  return certificates.certificates.map((document) => ({ id: document.payload.id }));
}

export async function generateMetadata({ params }: { params: Promise<Params> }): Promise<Metadata> {
  const { id } = await params;
  const document = certificateById(id);
  if (!document) return { title: "Certificate" };
  const { payload } = document;
  const description = metaDescription(
    `${SITE_NAME} ${tierLabel(payload.displayTier)} certificate for ${payload.subject.title}. ${payload.statusReason}`,
  );
  return siteMeta(`/cert/${payload.id}`, {
    title: `${payload.subject.title} certificate`,
    description,
    keywords: [payload.subject.title, "certificate", tierLabel(payload.displayTier)],
    image: `/cert/${payload.id}/opengraph-image`,
    imageAlt: `${payload.subject.title} certificate, ${tierLabel(payload.displayTier)}.`,
  });
}

export default async function CertificatePage({ params }: { params: Promise<Params> }) {
  const { id } = await params;
  const document = certificateById(id);
  if (!document) notFound();
  const { payload } = document;
  const markdown = embedMarkdown(document);
  const html = embedHtml(document);
  const entryHref = payload.subject.kind === "skill" ? `/skills/${payload.subject.name}` : `/agents/${payload.subject.name}`;
  const short = payload.sourceCommit.slice(0, 12);

  return (
    <ArticleFrame
      title={payload.subject.title}
      lede={`${tierLabel(payload.displayTier)} on ${SITE_NAME}. ${payload.statusReason}`}
      path={`/cert/${payload.id}`}
      crumbs={[
        { href: "/", label: "Home" },
        { href: "/certification", label: "Certification" },
        { label: payload.id },
      ]}
      structuredData={[
        {
          "@context": "https://schema.org",
          "@type": "CreativeWork",
          name: `${payload.subject.title} certificate`,
          description: payload.statusReason,
          url: absoluteUrl(`/cert/${payload.id}`),
          datePublished: payload.issuedAt,
          identifier: payload.id,
        },
      ]}
      plate={
        <aside className="plate" aria-label="Certificate facts">
          <p className="plate-name">{payload.id}</p>
          <dl>
            <dt>Tier</dt>
            <dd>{tierLabel(payload.displayTier)}</dd>
            <dt>Claimed</dt>
            <dd>{payload.claimedTier}</dd>
            <dt>Status</dt>
            <dd>{payload.status}</dd>
            <dt>Lint</dt>
            <dd>
              {payload.lint.score}
              <span className="quiet"> · {payload.lint.gate}</span>
            </dd>
            <dt>Issued</dt>
            <dd>
              <time dateTime={payload.issuedAt}>{formatDropDate(payload.issuedAt)}</time>
            </dd>
            <dt>Expires</dt>
            <dd>
              <time dateTime={payload.expiresAt}>{formatDropDate(payload.expiresAt)}</time>
            </dd>
            <dt>Commit</dt>
            <dd>
              <a href={`${REPO_URL}/commit/${payload.sourceCommit}`}>{short}</a>
              <span className="break-id">{payload.sourceCommit}</span>
            </dd>
            <dt>Digest</dt>
            <dd className="break-id">{payload.contentDigest}</dd>
            <dt>Signature</dt>
            <dd>{document.signed ? "Ed25519" : "Unsigned"}</dd>
          </dl>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img className="cert-badge" src={`/badge/${payload.id}.svg`} alt={badgeAlt(document)} width={payload.badge.width} height={payload.badge.height} />
        </aside>
      }
    >
      <Contents
        items={[
          { id: "what-was-checked", text: "What was checked", depth: 2 },
          { id: "review", text: "Review", depth: 2 },
          { id: "revalidation", text: "Revalidation", depth: 2 },
          { id: "embed", text: "Embed", depth: 2 },
          { id: "verify", text: "Verify", depth: 2 },
          { id: "limits", text: "Limits", depth: 2 },
        ]}
      />
      <div className="wiki-prose">
        <section id="what-was-checked">
          <h2>What was checked</h2>
          <p>{payload.lint.summary}</p>
          <p>
            Score {payload.lint.score}. {payload.lint.errors} errors, {payload.lint.warnings} warnings, {payload.lint.info} notes.
          </p>
          {payload.checks.length === 0 ? (
            <p>No install probe and no eval are recorded for this certificate. Listed does not mean the entry was executed.</p>
          ) : (
            <ul className="entry-list">
              {payload.checks.map((check) => (
                <li key={check.id}>
                  <p>
                    {check.kind} <code>{check.id}</code> — {check.ok ? "passed" : "failed"}
                  </p>
                  <pre className="snippet">
                    <code>{check.stdout || check.stderr || "—"}</code>
                  </pre>
                </li>
              ))}
            </ul>
          )}
          {payload.run.ranAt ? (
            <p>
              The harness recorded this run at <time dateTime={payload.run.ranAt}>{payload.run.ranAt}</time>.
              {payload.run.countsAsVerification
                ? " It counts toward Verified."
                : " It does not count toward Verified on this certificate."}
            </p>
          ) : null}
        </section>

        <section id="review">
          <h2>Review</h2>
          {payload.review ? (
            <>
              <p>
                {payload.review.reviewer} on <time dateTime={payload.review.date}>{formatDropDate(payload.review.date)}</time>.
              </p>
              <p>{payload.review.notes}</p>
            </>
          ) : (
            <p>No human review is recorded. Certified is the only tier that requires a reviewer, a date, and notes in the repository.</p>
          )}
        </section>

        <section id="revalidation">
          <h2>Revalidation</h2>
          <p>{payload.revalidation.sourceRule}</p>
          <p>{payload.revalidation.expiryRule}</p>
          {payload.currentCommit !== payload.sourceCommit ? (
            <p>
              The entry&apos;s latest commit is{" "}
              <a href={`${REPO_URL}/commit/${payload.currentCommit}`}>{payload.currentCommit.slice(0, 12)}</a>. This
              certificate stays on {short} until it is re-checked.
            </p>
          ) : (
            <p>The recorded commit is still the latest commit of this entry.</p>
          )}
        </section>

        <section id="embed">
          <h2>Embed</h2>
          <p>Paste either snippet into a README or a website. The image is the badge. The link opens this page.</p>
          <p className="embed-preview">
            <a href={`/cert/${payload.id}`}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={`/badge/${payload.id}.svg`} alt={badgeAlt(document)} width={payload.badge.width} height={payload.badge.height} />
            </a>
          </p>
          <p>
            Markdown <CopyButton text={markdown} />
          </p>
          <pre className="snippet">
            <code>{markdown}</code>
          </pre>
          <p>
            HTML <CopyButton text={html} />
          </p>
          <pre className="snippet">
            <code>{html}</code>
          </pre>
        </section>

        <section id="verify">
          <h2>Verify</h2>
          <p>
            The machine-readable record is <a href={payload.urls.record}>{payload.urls.record}</a>. The public
            key is <a href={payload.urls.publicKey}>{payload.urls.publicKey}</a>.
            {document.signed
              ? " This build signed the canonical payload with Ed25519."
              : " This build left the record unsigned because AGENTPEDIA_SIGNING_KEY was unset. The signature field is null on purpose."}
          </p>
          <pre className="snippet">
            <code>{`node tools/verify_cert.mjs ${payload.urls.record}`}</code>
          </pre>
          <p>
            Exit 0 means the signature matches the canonical payload and the pinned public key. Exit 2 means the record
            is unsigned. Exit 1 means the signature does not match.
          </p>
        </section>

        <section id="limits">
          <h2>Limits</h2>
          <ul>
            {payload.limits.map((limit) => (
              <li key={limit}>{limit}</li>
            ))}
          </ul>
          <p>
            The full explanation of the tiers is on <Link href="/certification">Certification</Link>. The entry itself is{" "}
            <Link href={entryHref}>{payload.subject.title}</Link>.
          </p>
        </section>
      </div>
    </ArticleFrame>
  );
}
