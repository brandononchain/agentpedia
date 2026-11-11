import type { MetadataRoute } from "next";
import { certificates } from "@/lib/certificates";
import { catalog } from "@/lib/catalog";
import { SITE_ORIGIN } from "@/lib/site";

export default function sitemap(): MetadataRoute.Sitemap {
  const origin = SITE_ORIGIN;
  const now = new Date(catalog.generatedAt);
  const staticRoutes = ["", "/browse", "/agents", "/lint", "/changelog", "/az", "/glossary", "/certification", "/certify"].map((path) => ({
    url: `${origin}${path || "/"}`,
    lastModified: now,
  }));
  const categories = catalog.categories.map((category) => ({
    url: `${origin}/category/${category.id}`,
    lastModified: now,
  }));
  const skills = catalog.skills.map((skill) => ({
    url: `${origin}/skills/${skill.name}`,
    lastModified: new Date(`${skill.added}T00:00:00Z`),
  }));
  const agents = catalog.agents.map((agent) => ({
    url: `${origin}/agents/${agent.name}`,
    lastModified: new Date(`${agent.added}T00:00:00Z`),
  }));
  const certs = certificates.certificates.map((document) => ({
    url: `${origin}/cert/${document.payload.id}`,
    lastModified: new Date(`${document.payload.issuedAt}T00:00:00Z`),
  }));
  return [...staticRoutes, ...categories, ...skills, ...agents, ...certs];
}
