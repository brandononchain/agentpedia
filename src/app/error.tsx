"use client";

export default function ErrorPage({ reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <div className="page-wrap" style={{ padding: "3rem 0" }}>
      <h1 className="entry-title">This page did not render</h1>
      <p className="lede">The view failed. The catalog files are unchanged. Try the page again, or go back to search.</p>
      <p style={{ marginTop: "1rem", display: "flex", gap: "1rem" }}>
        <button type="button" className="solid-button" onClick={() => reset()}>
          Try again
        </button>
        <a href="/browse">Search</a>
      </p>
    </div>
  );
}
