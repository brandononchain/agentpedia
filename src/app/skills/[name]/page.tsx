import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArticleFrame } from "@/components/article-frame";
import { CertFact } from "@/components/cert-fact";
import { Contents } from "@/components/contents";
import { InstallPanel } from "@/components/install-panel";
import { MarkdownBody } from "@/components/markdown-body";
import { ScoreMark } from "@/components/score-mark";
import { catalog, getSkill } from "@/lib/catalog";
import { certificateFor, tierLabel } from "@/lib/certificates";
import { metaDescription } from "@/lib/seo";
import { absoluteUrl, siteMeta } from "@/lib/site";
import { formatBytes, formatDropDate, stripTitle } from "@/lib/format";
import { agentForSkill, extractToc, relatedSkills, shelfNeighbors, type TocItem } from "@/lib/wiki";

type Params = { name: string };

export const dynamicParams = false;

export function generateStaticParams() {
  return catalog.skills.map((skill) => ({ name: skill.name }));
}

export async function generateMetadata({ params }: { params: Promise<Params> }): Promise<Metadata> {
  const { name } = await params;
  const skill = getSkill(name);
  if (!skill) return { title: "Entry" };
  const description = metaDescription(skill.description);
  const tier = certificateFor("skill", skill.name);
  return siteMeta(`/skills/${skill.name}`, {
    title: skill.title,
    description,
    keywords: [skill.title, skill.categoryLabel, "agent skill", ...skill.tags].slice(0, 8),
    image: `/skills/${skill.name}/opengraph-image`,
    imageAlt: `${skill.title}, a ${skill.categoryLabel} skill. Lint score ${skill.lint.score}. ${tier ? tierLabel(tier.payload.displayTier) : "Unlisted"}.`,
  });
}

export default async function SkillPage({ params }: { params: Promise<Params> }) {
  const { name } = await params;
  const skill = getSkill(name);
  if (!skill) notFound();

  const agent = agentForSkill(skill.name);
  const tier = certificateFor("skill", skill.name);
  const related = relatedSkills(skill);
  const { prev, next } = shelfNeighbors(skill);
  const body = stripTitle(skill.body);
  const toc: TocItem[] = [
    ...extractToc(body),
    { id: "lint-report", text: "Lint report", depth: 2 },
    ...(related.length ? [{ id: "see-also", text: "See also", depth: 2 as const }] : []),
    { id: "references", text: "References", depth: 2 },
  ];

  return (
    <ArticleFrame
      current={`/category/${skill.category}`}
      title={skill.title}
      lede={skill.description}
      path={`/skills/${skill.name}`}
      crumbs={[
        { href: "/", label: "Home" },
        { href: "/#shelves", label: "Shelves" },
        { href: `/category/${skill.category}`, label: skill.categoryLabel },
        { label: skill.title },
      ]}
      structuredData={[
        {
          "@context": "https://schema.org",
          "@type": ["SoftwareSourceCode", "CreativeWork"],
          name: skill.title,
          description: skill.description,
          url: absoluteUrl(`/skills/${skill.name}`),
          codeRepository: catalog.repoUrl,
          programmingLanguage: "Markdown",
          license: skill.license || undefined,
          datePublished: skill.added,
          keywords: skill.tags.join(", "),
          isPartOf: { "@type": "CreativeWork", name: skill.categoryLabel, url: absoluteUrl(`/category/${skill.category}`) },
          additionalProperty: [
            { "@type": "PropertyValue", name: "lintScore", value: skill.lint.score },
            { "@type": "PropertyValue", name: "certificate", value: tier ? tierLabel(tier.payload.displayTier) : "unlisted" },
          ],
        },
      ]}
      plate={
        <aside className="plate" aria-label="Entry facts">
          <p className="plate-name">{skill.name}</p>
          <dl>
            <dt>Category</dt>
            <dd>
              <Link href={`/category/${skill.category}`}>{skill.categoryLabel}</Link>
            </dd>
            <dt>Agent</dt>
            <dd>
              {agent ? <Link href={`/agents/${agent.name}`}>{agent.name}</Link> : "Not bundled"}
            </dd>
            <dt>Lint</dt>
            <dd>
              <ScoreMark score={skill.lint.score} badge={skill.lint.badge} />
            </dd>
            <CertFact kind="skill" name={skill.name} />
            <dt>Version</dt>
            <dd>Not recorded</dd>
            <dt>Added</dt>
            <dd>
              <time dateTime={skill.added}>{formatDropDate(skill.added)}</time>
            </dd>
            <dt>License</dt>
            <dd>{skill.license || "Not recorded"}</dd>
            {skill.compatibility ? (
              <>
                <dt>Compatibility</dt>
                <dd>{skill.compatibility}</dd>
              </>
            ) : null}
            <dt>Tags</dt>
            <dd>
              <ul className="tag-list">
                {skill.tags.map((tag) => (
                  <li key={tag}>
                    <Link href={`/browse?tag=${encodeURIComponent(tag)}`}>{tag}</Link>
                  </li>
                ))}
              </ul>
            </dd>
          </dl>
          <h2>Install</h2>
          <InstallPanel install={skill.install} />
        </aside>
      }
    >
      <Contents items={toc} />
      <MarkdownBody source={body} selfHref={`/skills/${skill.name}`} />

      <section className="see-also" id="lint-report">
        <h2 className="section-title">Lint report</h2>
        <p className="quiet" style={{ marginTop: "0.45rem" }}>
          Score {skill.lint.score}. {skill.lint.errors} errors, {skill.lint.warnings} warnings, {skill.lint.info} notes.
        </p>
        {skill.lint.findings.length === 0 ? (
          <p style={{ marginTop: "0.45rem" }}>skill-lint reported no errors, warnings, or notes.</p>
        ) : (
          <ul className="entry-list">
            {skill.lint.findings.map((finding) => (
              <li key={`${finding.ruleId}-${finding.line}`}>
                <span className="quiet">
                  {finding.severity} · {finding.ruleId}
                  {finding.line ? `:${finding.line}` : ""}
                </span>
                <span> {finding.message}</span>
                <span className="quiet"> {finding.hint}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      {related.length > 0 ? (
        <section className="see-also" id="see-also">
          <h2 className="section-title">See also</h2>
          <ul>
            {agent ? (
              <li>
                <Link href={`/agents/${agent.name}`}>{agent.name}</Link>
                <span className="quiet">, the agent that bundles this skill</span>
              </li>
            ) : null}
            {related.map((item) => (
              <li key={item.name}>
                <Link href={`/skills/${item.name}`}>{item.title}</Link>
                <span className="quiet"> {item.categoryLabel}</span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <section className="refs" id="references">
        <h2 className="section-title">References</h2>
        <ul>
          <li>
            Source path <span className="snippet" style={{ display: "inline", border: 0, background: "transparent", padding: 0 }}>{skill.sourcePath}</span>
          </li>
          {skill.files.map((file) => (
            <li key={file.path}>
              <a href={file.url}>{file.path}</a>
              <span className="quiet"> {formatBytes(file.bytes)}</span>
            </li>
          ))}
          <li>
            <a href={skill.rawUrl}>Raw SKILL.md</a>
          </li>
          <li>
            <a href={skill.zipUrl}>Download the skill folder</a>
          </li>
          <li>
            <a href={catalog.specUrl}>Agent Skills specification</a>
          </li>
        </ul>
      </section>

      <nav className="pager" aria-label="Nearby entries">
        <div>
          {prev ? (
            <Link href={`/skills/${prev.name}`} rel="prev">
              <span className="quiet">Previous</span>
              <span style={{ display: "block" }}>{prev.title}</span>
            </Link>
          ) : (
            <span className="quiet">Start of this shelf</span>
          )}
        </div>
        <div className="pager-next">
          {next ? (
            <Link href={`/skills/${next.name}`} rel="next">
              <span className="quiet">Next</span>
              <span style={{ display: "block" }}>{next.title}</span>
            </Link>
          ) : (
            <span className="quiet">End of this shelf</span>
          )}
        </div>
      </nav>
    </ArticleFrame>
  );
}
