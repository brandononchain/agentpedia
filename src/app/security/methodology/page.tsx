import type { Metadata } from "next";
import Link from "next/link";
import { ArticleFrame } from "@/components/article-frame";
import { Contents } from "@/components/contents";
import { catalog } from "@/lib/catalog";
import { SITE_NAME, siteMeta } from "@/lib/site";

export const metadata: Metadata = siteMeta("/security/methodology", {
  title: "Audit methodology",
  description: `What the ${SITE_NAME} static audit checks, how the score is calculated, and what it does not run.`,
  keywords: ["security audit", "methodology", SITE_NAME],
});

const SOURCES = [
  ["Snyk ToxicSkills", "https://research.snyk.io/blog/skill-analysis/"],
  ["The Devil Wears Markdown", "https://arxiv.org/abs/2611.10830"],
  ["VirusTotal, hidden instructions", "https://blog.virustotal.com/2026/10/how-some-malicious-ai-skills-hide.html"],
  ["Trojan Source", "https://arxiv.org/abs/2111.00169"],
  ["Unicode tags", "https://embracethered.com/blog/posts/2024/hiding-and-finding-text-with-unicode-tags/"],
  [
    "OWASP Top 10 for Agentic Applications",
    "https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/",
  ],
  ["OWASP LLM Top 10", "https://owasp.org/www-project-top-10-for-large-language-model-applications/"],
  ["MCP tool poisoning", "https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks"],
  ["skills-lock hash", "https://github.com/vercel-labs/skills/blob/main/src/skill-hash.ts"],
];

export default function MethodologyPage() {
  const audit = catalog.audit;
  return (
    <ArticleFrame
      title="Audit methodology"
      lede="Phase 1 reads the files. It does not run the skill, and it does not claim the entry is safe against a hostile user."
      path="/security/methodology"
      crumbs={[
        { href: "/", label: "Home" },
        { href: "/security", label: "Security" },
        { label: "Methodology" },
      ]}
    >
      <Contents
        items={[
          { id: "checks", text: "Checks", depth: 2 },
          { id: "score", text: "Score", depth: 2 },
          { id: "tiers", text: "Tiers", depth: 2 },
          { id: "later", text: "Later phases", depth: 2 },
          { id: "sources", text: "Sources", depth: 2 },
        ]}
      />
      <div className="wiki-prose">
        <section id="checks">
          <h2>Checks</h2>
          <p>
            The auditor is {audit?.auditor ?? "agentpedia-audit"}, ruleset {audit?.rulesetVersion ?? "1.0.0"}. Rules in
            family S read skill and agent text. Family C reads bundled code. Family D reads dependency files. A finding
            names a rule, a severity, a file, a line, a short snippet, and a remediation. Hidden characters in a snippet
            are escaped so the page cannot render them.
          </p>
          {audit ? (
            <div className="table-scroll" tabIndex={0}>
              <table>
                <thead>
                  <tr>
                    <th>Rule</th>
                    <th>Severity</th>
                    <th>What it looks for</th>
                  </tr>
                </thead>
                <tbody>
                  {audit.rules.map((rule) => (
                    <tr key={rule.id}>
                      <td>{rule.id}</td>
                      <td>{rule.severity}</td>
                      <td>{rule.summary}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p>Rebuild the catalog to list the rules.</p>
          )}
        </section>
        <section id="score">
          <h2>Score</h2>
          <p>
            The score starts at 100. A critical finding costs {audit?.weights.critical ?? 40}, a high finding{" "}
            {audit?.weights.high ?? 18}, a medium finding {audit?.weights.medium ?? 8}, a low finding{" "}
            {audit?.weights.low ?? 3}, and an info finding {audit?.weights.info ?? 1}. The result is never below 0.
          </p>
          <p>
            Grade F means any critical finding, or a score below 60. Otherwise D is below 70, C is below 80, B is below
            90, and A is 90 or above.
          </p>
          <p>
            Status is on hold when the grade is F, any finding is critical, or a high finding is past its grace period.
            Grace is {audit?.graceDays ?? 14} days from the first day the finding was seen. The date is stored in{" "}
            <code>data/audit-grace.json</code> and does not reset when the line number moves. A high finding inside
            grace is a warning. Anything else passed. The audit expires {audit?.auditDays ?? 90} days after the day it
            ran. CVE lookup is off unless <code>AGENTPEDIA_AUDIT_OSV=1</code>, and even then the client is a stub.
          </p>
        </section>
        <section id="tiers">
          <h2>Tiers</h2>
          <p>
            Listed requires a lint score of 100 and an audit that is not on hold. A warning can still be listed. On
            hold is not listed. The badge says the grade, or “on hold”. Verified still requires the recorded check
            harness. Certified still requires a named review, and that reviewer cannot be the entry’s author when an
            author login is recorded. A changed content digest voids the previous audit. The build audits the current
            files. <Link href="/certification">Certification</Link> states the same rules.
          </p>
        </section>
        <section id="later">
          <h2>Later phases</h2>
          <p>
            Each report records four stages. Only static analysis runs. Phase 2 is a sandbox with no network and canary
            credentials. Phase 3 is a prompt-injection red team against mock tools. Phase 4 is a manual review the
            author cannot give themselves. Those three are not gates.
          </p>
        </section>
        <section id="sources">
          <h2>Sources</h2>
          <ul>
            {SOURCES.map(([label, href]) => (
              <li key={href}>
                <a href={href}>{label}</a>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </ArticleFrame>
  );
}
