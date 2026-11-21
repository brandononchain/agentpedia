import { SkillCatalog, memorySkillFiles } from "@modelcontextprotocol/server/ext/skills";
import { entryFiles } from "@/lib/brain/content";
import { loadBrainIndex } from "@/lib/brain/index";
import { isServable } from "@/lib/brain/trust";

let catalogPromise: Promise<SkillCatalog> | null = null;

/** SEP-2640 catalog. Only served skills. SKILL.md includes the provenance header. */
export function brainSkillCatalog() {
  if (!catalogPromise) {
    catalogPromise = (async () => {
      const index = loadBrainIndex();
      const files: Record<string, string | Uint8Array> = {};
      for (const entry of index.entries) {
        if (entry.kind !== "skill" || !isServable(entry)) continue;
        for (const file of entryFiles(entry)) {
          const key = `${entry.name}/${file.path}`;
          if (file.text !== undefined) files[key] = file.text;
          else if (file.blob) files[key] = new Uint8Array(file.blob);
        }
      }
      return SkillCatalog.load(memorySkillFiles(files), {
        cacheHint: { ttlMs: 300_000, cacheScope: "public" },
        pageSize: 50,
        onWarning: (warning) => {
          console.warn(`brain skills: ${warning.path}: ${warning.message}`);
        },
      });
    })();
  }
  return catalogPromise;
}

export function resetBrainSkillCatalog() {
  catalogPromise = null;
}
