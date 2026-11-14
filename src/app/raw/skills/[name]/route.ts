import { catalog, getSkill } from "@/lib/catalog";
import { readSkillMarkdown } from "@/lib/machine";

export const dynamic = "force-static";

export function generateStaticParams() {
  return catalog.skills.map((skill) => ({ name: skill.name }));
}

export async function GET(_request: Request, context: { params: Promise<{ name: string }> }) {
  const { name } = await context.params;
  const skill = getSkill(name);
  if (!skill) return new Response("Not found\n", { status: 404 });
  return new Response(readSkillMarkdown(skill), {
    headers: { "content-type": "text/markdown; charset=utf-8" },
  });
}
