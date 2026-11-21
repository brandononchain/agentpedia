import type { Metadata } from "next";
import Link from "next/link";
import { ArticleFrame } from "@/components/article-frame";
import { certificates } from "@/lib/certificates";
import { catalog } from "@/lib/catalog";
import { SITE_IDENTITY, SITE_NOT } from "@/lib/structured";
import { SITE_NAME, siteMeta } from "@/lib/site";

export const metadata: Metadata = siteMeta("/compare/skills-sh", {
  title: "Agentpedia vs skills.sh",
  description: `${SITE_NAME} audits and grades every entry and publishes certificate tiers. skills.sh is a large open directory with an install CLI and says it cannot guarantee every skill's security.`,
  keywords: ["Agentpedia", "skills.sh", "agent skills", "SKILL.md"],
});

const SKILLS_HOME = "https://skills.sh";
const SKILLS_DOCS = "https://skills.sh/docs";
const SKILLS_ABOUT = "https://skills.sh/about";
const SKILLS_CLI = "https://github.com/vercel-labs/skills";

export default function CompareSkillsShPage() {
  const { stats } = catalog;
  const tiers = certificates.stats;
  const audit = catalog.audit?.stats;

  return (
    <ArticleFrame
      title="Agentpedia vs skills.sh"
      lede="Both sites publish SKILL.md files for AI agents. They check those files differently, and neither one is a promise that a skill is safe to run."
      path="/compare/skills-sh"
      crumbs={[
        { href: "/", label: "Home" },
        { label: "Agentpedia vs skills.sh" },
      ]}
    >
      <div className="wiki-prose">
        <p>
          {SITE_IDENTITY} {SITE_NOT}
        </p>

        <section id="agentpedia">
          <h2>Agentpedia</h2>
          <p>
            Agentpedia audits and grades every published entry. skill-lint scores each skill. The static audit then
            assigns a letter grade. A book title uses that score and that grade from the catalog. An agent is graded
            on its own audit. The build does not publish a skill with a lint error or a warning, and an audit of on
            hold is not listed.
          </p>
          <p>
            This build has {stats.skills} skills, {stats.agents} agents, and {stats.categories} shelves.
            {audit
              ? ` The audit summary is ${audit.passed} passed, ${audit.warning} warning, and ${audit.onHold} on hold.`
              : ""}{" "}
            Certificates record a tier on that same tree: {tiers.listed} listed, {tiers.verified} verified, and{" "}
            {tiers.certified} certified. Listed is the lint gate plus an audit that is not on hold. Verified adds a
            recorded check run. Certified adds a named review. Phase 1 of the audit reads the files. It does not
            execute the entry.
          </p>
          <ul>
            <li>
              <Link href="/">Agentpedia home</Link>
            </li>
            <li>
              <Link href="/security">Security grades</Link>
            </li>
            <li>
              <Link href="/security/methodology">Audit methodology</Link>
            </li>
            <li>
              <Link href="/certification">Certificate tiers</Link>
            </li>
            <li>
              <Link href="/lint">How we lint</Link>
            </li>
          </ul>
        </section>

        <section id="skills-sh">
          <h2>skills.sh</h2>
          <p>
            <a href={SKILLS_HOME}>skills.sh</a> is an open directory of agent skills. The skills CLI installs a skill
            with one command, for example <code>npx skills add vercel-labs/agent-skills</code>. The CLI is open source
            at <a href={SKILLS_CLI}>github.com/vercel-labs/skills</a>. Its leaderboard ranks skills from anonymous
            install telemetry collected by that CLI.
          </p>
          <p>
            skills.sh says it runs routine security audits. It also says it cannot guarantee every skill. From its
            documentation: “We do our best to maintain a safe ecosystem, but we cannot guarantee the quality or
            security of every skill listed on skills.sh.”
          </p>
          <ul>
            <li>
              <a href={SKILLS_HOME}>skills.sh</a>
            </li>
            <li>
              <a href={SKILLS_DOCS}>skills.sh documentation</a>, including the security note and the install command
            </li>
            <li>
              <a href={SKILLS_ABOUT}>About skills.sh</a>
            </li>
          </ul>
        </section>

        <section id="which">
          <h2>Using either one</h2>
          <p>
            Use Agentpedia to read an entry that has a lint score, an audit grade, and a public certificate. Use
            skills.sh to browse a large directory and install a skill with the CLI. Read the SKILL.md before installing
            from either site.
          </p>
        </section>
      </div>
    </ArticleFrame>
  );
}
