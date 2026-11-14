import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { ImageResponse } from "next/og";
import { SITE_TAGLINE } from "@/lib/site";

export const ogSize = { width: 1200, height: 630 };

type Font = { name: string; data: Buffer; weight: 400 | 600 | 700; style: "normal" };

let fonts: Font[] | null = null;

async function ogFonts() {
  if (fonts) return fonts;
  const dir = join(process.cwd(), "src/fonts");
  const [serif, sans, bold] = await Promise.all([
    readFile(join(dir, "Literata-600.ttf")),
    readFile(join(dir, "Atkinson-Regular.ttf")),
    readFile(join(dir, "Atkinson-Bold.ttf")),
  ]);
  fonts = [
    { name: "Literata", data: serif, weight: 600, style: "normal" },
    { name: "Atkinson", data: sans, weight: 400, style: "normal" },
    { name: "Atkinson", data: bold, weight: 700, style: "normal" },
  ];
  return fonts;
}

function titleSize(title: string) {
  if (title.length > 48) return 52;
  if (title.length > 32) return 64;
  return 76;
}

export async function renderOg(input: {
  kicker?: string;
  title: string;
  lines?: string[];
}) {
  const loaded = await ogFonts();
  const lines = input.lines ?? [];
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          background: "#f4efe4",
          color: "#1c1915",
          padding: "72px",
        }}
      >
        {input.kicker ? (
          <div
            style={{
              display: "flex",
              fontFamily: "Atkinson",
              fontWeight: 700,
              fontSize: 24,
              letterSpacing: "0.14em",
              textTransform: "uppercase",
              color: "#0e4f57",
              marginBottom: 28,
            }}
          >
            {input.kicker}
          </div>
        ) : null}
        <div
          style={{
            display: "flex",
            fontFamily: "Literata",
            fontWeight: 600,
            fontSize: input.kicker ? titleSize(input.title) : 92,
            letterSpacing: "-1.5px",
            lineHeight: 1.05,
            textAlign: "center",
            maxWidth: 1000,
          }}
        >
          {input.title}
        </div>
        <div style={{ display: "flex", width: 220, height: 3, background: "#0e4f57", marginTop: 32 }} />
        {lines.map((line) => (
          <div
            key={line}
            style={{
              display: "flex",
              fontFamily: "Atkinson",
              fontSize: 30,
              color: "#534e45",
              marginTop: 26,
              textAlign: "center",
              maxWidth: 980,
            }}
          >
            {line}
          </div>
        ))}
        <div
          style={{
            display: "flex",
            fontFamily: "Atkinson",
            fontWeight: 700,
            fontSize: 26,
            color: "#0e4f57",
            marginTop: 48,
          }}
        >
          agentpedia.sh
        </div>
      </div>
    ),
    { ...ogSize, fonts: loaded },
  );
}

export async function homeOg(statsLine: string) {
  return renderOg({ title: "Agentpedia", lines: [SITE_TAGLINE, statsLine] });
}
