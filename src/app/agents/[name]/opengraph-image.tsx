import { catalog, getAgent } from "@/lib/catalog";
import { certificateFor, tierLabel } from "@/lib/certificates";
import { ogSize, renderOg } from "@/lib/og";

export const runtime = "nodejs";
export const size = ogSize;
export const contentType = "image/png";
export const alt = "Agent entry";

export default async function Image({ params }: { params: Promise<{ name: string }> }) {
  const { name } = await params;
  const agent = getAgent(name);
  if (!agent) return renderOg({ title: "Agentpedia", lines: ["Missing entry"] });
  const tier = certificateFor("agent", agent.name);
  return renderOg({
    kicker: agent.callNumber,
    title: agent.name,
    lines: [
      `${agent.subshelfLabel} · ${agent.categoryLabel}`,
      `${agent.skills.length} skills · ${tier ? tierLabel(tier.payload.displayTier) : "unlisted"}`,
    ],
  });
}

export function generateStaticParams() {
  return catalog.agents.map((agent) => ({ name: agent.name }));
}
