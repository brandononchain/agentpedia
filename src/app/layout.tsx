import type { Metadata } from "next";
import { Fraunces, Geist_Mono, Outfit } from "next/font/google";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";
import "./globals.css";

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-outfit",
});

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-fraunces",
});

const mono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
});

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "http://127.0.0.1:43123";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "Skilldex",
    template: "%s · Skilldex",
  },
  description:
    "A curated directory of Agent Skills and agents. Every entry is linted and safety-checked before it ships.",
  authors: [{ name: "Brandon", url: "https://brandononchain.com" }],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`dark ${outfit.variable} ${fraunces.variable} ${mono.variable}`}>
      <body className="min-h-screen antialiased">
        <a
          href="#content"
          className="sr-only focus:not-sr-only focus:absolute focus:top-3 focus:left-3 focus:z-50 focus:bg-background focus:px-3 focus:py-2"
        >
          Skip to content
        </a>
        <SiteHeader />
        <main id="content">{children}</main>
        <SiteFooter />
      </body>
    </html>
  );
}
