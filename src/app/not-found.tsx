import Link from "next/link";

export default function NotFound() {
  return (
    <div className="mx-auto max-w-3xl px-5 py-24">
      <h1 className="font-serif text-5xl font-light tracking-tight">That entry is not on the shelf.</h1>
      <p className="mt-4 text-muted-foreground">
        The name does not match a skill or an agent in this build. It may have been renamed, or it never shipped.
      </p>
      <p className="mt-6 flex gap-5 text-sm">
        <Link href="/browse" className="text-stamp underline decoration-stamp/40 underline-offset-4">
          Browse skills
        </Link>
        <Link href="/agents" className="text-stamp underline decoration-stamp/40 underline-offset-4">
          Browse agents
        </Link>
      </p>
    </div>
  );
}
