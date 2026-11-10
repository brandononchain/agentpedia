"use client";

import { useState } from "react";
import { CopyButton } from "@/components/copy-button";
import type { InstallTarget } from "@/lib/catalog";

const ORDER = ["claude", "codex", "cursor", "grok"] as const;

export function InstallPanel({ install }: { install: Record<(typeof ORDER)[number], InstallTarget> }) {
  const [current, setCurrent] = useState<(typeof ORDER)[number]>("claude");
  const target = install[current];

  return (
    <div>
      <div className="install-tabs" role="tablist" aria-label="Install target">
        {ORDER.map((key) => (
          <button
            key={key}
            type="button"
            role="tab"
            id={`install-tab-${key}`}
            aria-selected={current === key}
            aria-controls={`install-panel-${key}`}
            tabIndex={current === key ? 0 : -1}
            onClick={() => setCurrent(key)}
            onKeyDown={(event) => {
              const index = ORDER.indexOf(key);
              if (event.key === "ArrowRight" || event.key === "ArrowLeft") {
                event.preventDefault();
                const next = ORDER[(index + (event.key === "ArrowRight" ? 1 : ORDER.length - 1)) % ORDER.length];
                setCurrent(next);
                document.getElementById(`install-tab-${next}`)?.focus();
              }
            }}
          >
            {install[key].label}
          </button>
        ))}
      </div>
      <div role="tabpanel" id={`install-panel-${current}`} aria-labelledby={`install-tab-${current}`}>
        <p className="quiet" style={{ marginTop: "0.55rem" }}>
          {target.hint}
        </p>
        <p style={{ marginTop: "0.45rem" }}>
          <CopyButton text={target.snippet} label="Copy install" />
        </p>
        <pre className="snippet">
          <code>{target.snippet}</code>
        </pre>
      </div>
    </div>
  );
}
