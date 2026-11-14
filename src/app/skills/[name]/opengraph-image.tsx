import { catalog, getSkill } from "@/lib/catalog";
import { certificateFor, tierLabel } from "@/lib/certificates";
import { ogSize, renderOg } from "@/lib/og";

export const runtime = "nodejs";
export const size = ogSize;
export const contentType = "image/png";
export const alt = "Skill entry";

export default async function Image({ params }: { params: Promise<{ name: string }> }) {
  const { name } = await params;
  const skill = getSkill(name);
  if (!skill) return renderOg({ title: "Agentpedia", lines: ["Missing entry"] });
  const tier = certificateFor("skill", skill.name);
  return renderOg({
    kicker: "Skill",
    title: skill.title,
    lines: [
      skill.categoryLabel,
      `Lint ${skill.lint.score} · ${tier ? tierLabel(tier.payload.displayTier) : "unlisted"}`,
    ],
  });
}

export function generateStaticParams() {
  return catalog.skills.map((skill) => ({ name: skill.name }));
}
