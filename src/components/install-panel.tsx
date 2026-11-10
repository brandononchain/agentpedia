"use client";

import { CopyButton } from "@/components/copy-button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { InstallTarget } from "@/lib/catalog";

const ORDER = ["claude", "codex", "cursor", "grok"] as const;

export function InstallPanel({
  install,
}: {
  install: Record<(typeof ORDER)[number], InstallTarget>;
}) {
  return (
    <Tabs defaultValue="claude">
      <TabsList variant="line" className="h-auto w-full flex-wrap justify-start gap-1 bg-transparent p-0">
        {ORDER.map((key) => (
          <TabsTrigger key={key} value={key} className="flex-none px-2 py-1">
            {install[key].label}
          </TabsTrigger>
        ))}
      </TabsList>
      {ORDER.map((key) => {
        const target = install[key];
        return (
          <TabsContent key={key} value={key} className="mt-4">
            <p className="text-sm text-muted-foreground">{target.hint}</p>
            <div className="mt-3 flex items-center justify-between gap-3">
              <p className="font-mono text-xs tracking-wide text-muted-foreground uppercase">
                Install
              </p>
              <CopyButton text={target.snippet} />
            </div>
            <pre className="mt-2 overflow-x-auto border border-border bg-background p-3 font-mono text-xs leading-relaxed text-foreground">
              <code>{target.snippet}</code>
            </pre>
          </TabsContent>
        );
      })}
    </Tabs>
  );
}
