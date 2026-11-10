import type { MetadataRoute } from "next";
import { catalog } from "@/lib/catalog";

export default function sitemap(): MetadataRoute.Sitemap {
  const origin = process.env.NEXT_PUBLIC_SITE_URL ?? "http://127.0.0.1:43123";
  const now = new Date(catalog.generatedAt);
  const staticRoutes = ["", "/browse", "/agents", "/lint", "/changelog", "/az", "/glossary"].map((path) => ({
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
  return [...staticRoutes, ...categories, ...skills, ...agents];
}
