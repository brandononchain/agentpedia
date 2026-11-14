import { catalog } from "@/lib/catalog";
import { homeOg } from "@/lib/og";

export const dynamic = "force-static";

export async function GET() {
  const { stats } = catalog;
  const image = await homeOg(`${stats.skills} skills · ${stats.agents} agents · ${stats.categories} shelves`);
  return image;
}
