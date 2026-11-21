import type { Metadata } from "next";
import Link from "next/link";
import { ArticleFrame } from "@/components/article-frame";
import { Contents } from "@/components/contents";
import { CopyButton } from "@/components/copy-button";
import { AGENT_PROMPT } from "@/lib/submit-spec";
import { REPO_URL, SITE_NAME, SITE_ORIGIN, siteMeta } from "@/lib/site";
import { howToLd, SUBMIT_HOWTO } from "@/lib/structured";

export const metadata: Metadata = siteMeta("/submit", {
  title: "Submit an entry",
  description: `How to submit a skill or an agent to ${SITE_NAME}, including a prompt a coding agent can follow.`,
  keywords: ["submit a skill", "agent skills", SITE_NAME],
});

export default function SubmitPage() {
  return (
    <ArticleFrame
      title="Submit an entry"
      lede="A skill or an agent starts as a pull request. There is no account and no form. The same steps work for a person or a coding agent."
      path="/submit"
      crumbs={[
        { href: "/", label: "Home" },
        { label: "Submit" },
      ]}
      structuredData={[howToLd(SITE_ORIGIN)]}
    >
      <Contents
        items={[
          { id: "person", text: "By hand", depth: 2 },
          { id: "agent", text: "With your agent", depth: 2 },
          { id: "checks", text: "What is checked", depth: 2 },
          { id: "hold", text: "On hold and warning", depth: 2 },
        ]}
      />
      <div className="wiki-prose">
        <section id="person">
          <h2>By hand</h2>
          <ol>
            <li id="step-1">
              <a href={REPO_URL}>Fork the Agentpedia repository</a>, or clone it and create a branch.
            </li>
            <li id="step-2">{SUBMIT_HOWTO.steps[1].text}</li>
          </ol>
          <pre className="snippet">
            <code>{`python3 tools/new_entry.py submit --kind skill \\
  --category <shelf> \\
  --subshelf <slug> \\
  --name <name> \\
  --description "<Third person. Use when the user asks for this job.>"`}</code>
          </pre>
          <p>
            An agent uses <code>--kind agent</code> and <code>--skills</code> with names that already exist.{" "}
            <code>python3 tools/new_entry.py shelves</code> lists shelves. The machine-readable spec is{" "}
            <Link href="/submit.md">/submit.md</Link>. The installable skill is{" "}
            <Link href="/skills/agentpedia-submit">agentpedia-submit</Link>.
          </p>
          <ol start={3}>
            <li id="step-3">{SUBMIT_HOWTO.steps[2].text}</li>
            <li id="step-4">{SUBMIT_HOWTO.steps[3].text}</li>
          </ol>
        </section>
        <section id="agent">
          <h2>With your agent</h2>
          <p>Paste this into Cursor, Claude Code, Codex, or another coding agent. It can follow the submission end to end.</p>
          <p>
            <CopyButton text={AGENT_PROMPT} label="Copy prompt" />
          </p>
          <pre className="snippet">
            <code>{AGENT_PROMPT}</code>
          </pre>
        </section>
        <section id="checks">
          <h2>What is checked</h2>
          <p>
            skill-lint must score 100. The static audit must be passed, or a warning while a high finding is still
            inside its grace period. Listed requires both. Verified also needs a recorded harness run. Certified also
            needs a named review, and the reviewer cannot be the recorded author. The phase 1 audit reads files. It
            does not run the entry. <Link href="/security/methodology">Methodology</Link> and{" "}
            <Link href="/certification">Certification</Link> say what each tier covers.
          </p>
        </section>
        <section id="hold">
          <h2>On hold and warning</h2>
          <p>
            On hold means a critical finding, grade F, or a high finding past grace. The entry is not listed. The
            report names the rule, the file, the line, and the change to make. A warning is a high finding still inside
            grace. It can be listed, and the page shows the days left. Fix the finding rather than deleting the rule.
          </p>
          <p>
            The certification workflow, including optional Verified checks, is on <Link href="/certify">Submit for certification</Link>.
          </p>
        </section>
      </div>
    </ArticleFrame>
  );
}
