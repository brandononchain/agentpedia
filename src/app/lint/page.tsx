import type { Metadata } from "next";
import { ArticleFrame } from "@/components/article-frame";
import { Contents } from "@/components/contents";
import { catalog } from "@/lib/catalog";
import { SITE_NAME } from "@/lib/site";
import { slugify, type TocItem } from "@/lib/wiki";

export const metadata: Metadata = {
  title: "How we lint",
  description: `The skill-lint rules ${SITE_NAME} runs before an entry can be listed, and how the score is calculated.`,
};

export default function LintPage() {
  const { scoring, stats } = catalog;
  const toc: TocItem[] = [
    { id: "the-score", text: "The score", depth: 2 },
    ...catalog.rules.map((group) => ({ id: slugify(group.group), text: group.group, depth: 2 as const })),
    { id: "references", text: "References", depth: 2 },
  ];

  return (
    <ArticleFrame
      title="How we lint"
      lede={`${SITE_NAME} lists a skill only after skill-lint reports no errors and no warnings. The score on an article is that check, not a rating of the advice inside.`}
      crumbs={[
        { href: "/", label: "Home" },
        { label: "How we lint" },
      ]}
    >
      <Contents items={toc} />
      <div className="wiki-prose">
        <p>
          Agent Skills are folders with a <code>SKILL.md</code> file. The format is an open specification, now a project
          of the Agentic AI Foundation under the Linux Foundation. The body is free Markdown, which is why quality
          varies so widely.
        </p>
        <p>
          In <a href={catalog.studyUrl}>From Anatomy to Smells</a>, Hong, Imani, and Ahmed at UC Irvine studied 238 real
          skills sampled from a public marketplace. Over 99 percent — 237 of the 238 — contained at least one skill
          smell. Smells introduced early rarely disappeared in later commits. Popularity did not clean them up.
        </p>
        <p>
          {SITE_NAME} vendors <code>tools/skill-lint</code>, a dependency-free Python checker for the spec, for
          progressive-disclosure smells, for broken relative links, and for a small set of safety patterns. The catalog
          build runs it on every skill. An error or a warning fails the build. Info findings are recorded and lower the
          score. This shelf has {stats.info} of them.
        </p>
        <h2 id="the-score">The score</h2>
        <p>
          A skill starts at {scoring.start}. Each error subtracts {scoring.errorPenalty}, each warning subtracts{" "}
          {scoring.warningPenalty}, and each info finding subtracts {scoring.infoPenalty}. The floor is {scoring.floor}.
          The badge reads clean when errors and warnings are both zero, noted when there are warnings but no errors, and
          blocked when any error remains. Blocked and noted entries do not ship in this catalog.
        </p>
        {catalog.rules.map((group) => (
          <section key={group.group}>
            <h2 id={slugify(group.group)}>{group.group}</h2>
            <div className="table-scroll">
              <table className="data-table">
                <caption className="sr-only">{group.group} rules</caption>
                <thead>
                  <tr>
                    <th scope="col">Rule</th>
                    <th scope="col">Severity</th>
                    <th scope="col">What it checks</th>
                  </tr>
                </thead>
                <tbody>
                  {group.rules.map((rule) => (
                    <tr key={rule.id}>
                      <th scope="row" style={{ fontFamily: "var(--font-mono)", fontWeight: 400, fontSize: "0.82rem" }}>
                        {rule.id}
                      </th>
                      <td>{rule.severity}</td>
                      <td>{rule.summary}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
        ))}
      </div>
      <section className="refs" id="references">
        <h2 className="section-title">References</h2>
        <ul>
          <li>
            <a href={catalog.studyUrl}>Hong, Imani, and Ahmed, From Anatomy to Smells</a>
          </li>
          <li>
            <a href={catalog.specUrl}>Agent Skills specification</a>
          </li>
          <li>
            <a href={catalog.aaifUrl}>Agentic AI Foundation</a>
          </li>
        </ul>
      </section>
    </ArticleFrame>
  );
}
