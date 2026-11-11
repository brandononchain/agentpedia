import type { Metadata } from "next";
import Link from "next/link";
import { ArticleFrame } from "@/components/article-frame";
import { Contents } from "@/components/contents";
import { REPO_URL, SITE_NAME, siteMeta } from "@/lib/site";

export const metadata: Metadata = {
  title: "Submit for certification",
  description: `How to submit a skill or agent to ${SITE_NAME} for a Listed or Verified certificate. No account and no form.`,
  ...siteMeta("/certify"),
};

export default function CertifyPage() {
  return (
    <ArticleFrame
      title="Submit for certification"
      lede={`There is no account and no form. A certificate starts as a pull request to ${SITE_NAME}. The maintainer records Listed or Verified from the checks that run on that pull request. Certified is a later human review, written into the repository.`}
      crumbs={[
        { href: "/", label: "Home" },
        { href: "/certification", label: "Certification" },
        { label: "Submit" },
      ]}
    >
      <Contents
        items={[
          { id: "pull-request", text: "Pull request", depth: 2 },
          { id: "checks", text: "Optional checks", depth: 2 },
          { id: "what-you-get", text: "What you get", depth: 2 },
        ]}
      />
      <div className="wiki-prose">
        <section id="pull-request">
          <h2>Pull request</h2>
          <ol>
            <li>
              Fork <a href={REPO_URL}>{REPO_URL}</a> and add the skill under <code>skills/&lt;category&gt;/&lt;name&gt;/</code>{" "}
              or, if you are not sure of the shelf, under <code>submissions/incoming/&lt;name&gt;/</code>. An agent goes
              under <code>agents/&lt;name&gt;/</code>.
            </li>
            <li>
              Follow the shape in <code>submissions/template/example-skill/</code> and the bar in{" "}
              <Link href="/lint">How we lint</Link>. The build refuses errors and warnings.
            </li>
            <li>
              Open a pull request and choose the certification template. Continuous integration lints the changed skill
              and posts the result on the pull request.
            </li>
          </ol>
          <p>
            A folder under <code>submissions/</code> is not published and does not receive a certificate until a
            maintainer moves it into <code>skills/</code>.
          </p>
        </section>
        <section id="checks">
          <h2>Optional checks</h2>
          <p>
            Verified needs a check manifest at <code>certs/checks/skill-&lt;name&gt;.json</code> (or{" "}
            <code>agent-&lt;name&gt;.json</code>). The manifest names the entry directory, an install probe of kind{" "}
            <code>copy-tree</code>, and at least one eval. Each eval is an argument list the harness runs inside the
            entry. The first argument is <code>python3</code> or a file inside the entry. Absolute paths and{" "}
            <code>..</code> are rejected.
          </p>
          <p>
            The certify workflow runs those evals and comments with the output. It writes{" "}
            <code>certs/results/</code> only when a maintainer runs the workflow with “write results”, or adds the{" "}
            <code>record-checks</code> label. A normal pull request does not commit a new timestamp on every push.
          </p>
          <p>
            The two recorded Verified skills in this repository are <Link href="/cert/skill-csv-profile">csv-profile</Link>{" "}
            and <Link href="/cert/skill-position-risk-sizer">position-risk-sizer</Link>. Their manifests are the pattern.
          </p>
        </section>
        <section id="what-you-get">
          <h2>What you get</h2>
          <p>
            After the entry is on the default branch and the catalog build passes, the site publishes{" "}
            <code>/cert/&lt;id&gt;</code>, <code>/badge/&lt;id&gt;.svg</code>, and <code>/cert/&lt;id&gt;.json</code>.
            The certificate page has the Markdown and HTML to embed. Listed is automatic for a score of 100. Verified
            waits for a real harness result. Certified waits for a person to add <code>review.reviewer</code>,{" "}
            <code>review.date</code>, and <code>review.notes</code> to the record.
          </p>
          <p>
            The tiers, the dates, and the things a certificate does not claim are on{" "}
            <Link href="/certification">Certification</Link>.
          </p>
        </section>
      </div>
    </ArticleFrame>
  );
}
