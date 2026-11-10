"use client";

import { useState } from "react";

export function CopyButton({ text, label = "Copy" }: { text: string; label?: string }) {
  const [message, setMessage] = useState(label);

  return (
    <button
      type="button"
      className="text-button"
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(text);
          setMessage("Copied");
        } catch {
          setMessage("Copy failed");
        }
        window.setTimeout(() => setMessage(label), 1600);
      }}
    >
      {message}
    </button>
  );
}
