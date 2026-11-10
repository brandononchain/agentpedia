"use client";

import { Button } from "@/components/ui/button";

export default function ErrorPage({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <div className="mx-auto max-w-3xl px-5 py-24">
      <h1 className="font-serif text-5xl font-light tracking-tight">This page did not render.</h1>
      <p className="mt-4 max-w-xl text-muted-foreground">
        Something in the view failed. The catalog files are unchanged. Try the page again, or go back to the shelf.
      </p>
      <div className="mt-6 flex gap-3">
        <Button type="button" className="rounded-sm" onClick={() => reset()}>
          Try again
        </Button>
        <a
          href="/browse"
          className="inline-flex h-8 items-center rounded-sm border border-border px-3 text-sm"
        >
          Browse
        </a>
      </div>
    </div>
  );
}
