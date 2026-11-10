"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";

export function CopyButton({
  text,
  label = "Copy",
}: {
  text: string;
  label?: string;
}) {
  const [message, setMessage] = useState(label);

  return (
    <Button
      type="button"
      variant="outline"
      size="sm"
      className="h-8 rounded-sm"
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
    </Button>
  );
}
