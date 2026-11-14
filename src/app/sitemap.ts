import type { MetadataRoute } from "next";
import { certificates } from "@/lib/certificates";
import { catalog } from "@/lib/catalog";
import { latestDate } from "@/lib/git-dates";
import { absoluteUrl } from "@/lib/site";

const STATIC_PAGES: { path: string; files: string[] }[] = [
  { path: "/", files: ["src/app/page.tsx", "data/catalog.json"] },
  { path: "/browse", files: ["src/app/browse/page.tsx", "src/components/browse-explorer.tsx"] },
  { path: "/agents", files: ["src/app/agents/page.tsx"] },
  { path: "/lint", files: ["src/app/lint/page.tsx"] },
  { path: "/changelog", files: ["src/app/changelog/page.tsx"] },
  { path: "/az", files: ["src/app/az/page.tsx"] },
  { path: "/glossary", files: ["src/app/glossary/page.tsx"] },
  { path: "/certification", files: ["src/app/certification/page.tsx"] },
  { path: "/certify", files: ["src/app/certify/page.tsx"] },
  { path: "/feed.xml", files: ["src/app/feed.xml/route.ts", "data/catalog.json"] },
  { path: "/atom.xml", files: ["src/app/atom.xml/route.ts", "data/catalog.json"] },
  { path: "/llms.txt", files: ["src/app/llms.txt/route.ts", "data/catalog.json"] },
  { path: "/llms-full.txt", files: ["src/app/llms-full.txt/route.ts", "skills", "agents"] },
  { path: "/catalog.json", files: ["src/app/catalog.json/route.ts", "data/catalog.json"] },
  { path: "/og.png", files: ["src/app/og.png/route.ts", "data/catalog.json"] },
];

export default function sitemap(): MetadataRoute.Sitemap {
  const fallback = catalog.generatedAt;
  const staticRoutes = STATIC_PAGES.map((page) => ({
    url: absoluteUrl(page.path),
    lastModified: latestDate(page.files, fallback),
  }));
  const categories = catalog.categories.map((category) => ({
    url: absoluteUrl(`/category/${category.id}`),
    lastModified: latestDate([`skills/${category.id}`, `src/app/category`], fallback),
  }));
  const skills = catalog.skills.flatMap((skill) => {
    const lastModified = latestDate([skill.sourcePath], `${skill.added}T00:00:00Z`);
    return [
      { url: absoluteUrl(`/skills/${skill.name}`), lastModified },
      { url: absoluteUrl(`/skills/${skill.name}.md`), lastModified },
    ];
  });
  const agents = catalog.agents.flatMap((agent) => {
    const lastModified = latestDate([agent.sourcePath], `${agent.added}T00:00:00Z`);
    return [
      { url: absoluteUrl(`/agents/${agent.name}`), lastModified },
      { url: absoluteUrl(`/agents/${agent.name}.md`), lastModified },
    ];
  });
  const certs = certificates.certificates.map((document) => ({
    url: absoluteUrl(`/cert/${document.payload.id}`),
    lastModified: latestDate(
      [`certs/records/${document.payload.id}.json`],
      `${document.payload.issuedAt}T00:00:00Z`,
    ),
  }));
  return [...staticRoutes, ...categories, ...skills, ...agents, ...certs];
}
