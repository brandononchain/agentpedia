import { catalog, getAgent } from "@/lib/catalog";
import { readAgentMarkdown } from "@/lib/machine";

export const dynamic = "force-static";

export function generateStaticParams() {
  return catalog.agents.map((agent) => ({ name: agent.name }));
}

export async function GET(_request: Request, context: { params: Promise<{ name: string }> }) {
  const { name } = await context.params;
  const agent = getAgent(name);
  if (!agent) return new Response("Not found\n", { status: 404 });
  return new Response(readAgentMarkdown(agent), {
    headers: { "content-type": "text/markdown; charset=utf-8" },
  });
}
