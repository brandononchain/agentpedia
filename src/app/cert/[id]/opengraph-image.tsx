import { certificateById, certificates, tierLabel } from "@/lib/certificates";
import { ogSize, renderOg } from "@/lib/og";

export const runtime = "nodejs";
export const size = ogSize;
export const contentType = "image/png";
export const alt = "Certificate";

export default async function Image({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const document = certificateById(id);
  if (!document) return renderOg({ title: "Agentpedia", lines: ["Missing certificate"] });
  const { payload } = document;
  return renderOg({
    kicker: "Certificate",
    title: payload.subject.title,
    lines: [tierLabel(payload.displayTier), payload.subject.kind === "skill" ? "Skill" : "Agent"],
  });
}

export function generateStaticParams() {
  return certificates.certificates.map((document) => ({ id: document.payload.id }));
}
