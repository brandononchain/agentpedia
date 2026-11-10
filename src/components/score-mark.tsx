import { Badge } from "@/components/ui/badge";
import type { BadgeName } from "@/lib/catalog";
import { cn } from "@/lib/utils";

const tone: Record<BadgeName, string> = {
  clean: "border-pass/70 text-pass",
  noted: "border-warn/70 text-warn",
  blocked: "border-stamp/70 text-stamp",
};

export function ScoreMark({
  score,
  badge,
  className,
}: {
  score: number;
  badge: BadgeName;
  className?: string;
}) {
  return (
    <Badge
      variant="outline"
      className={cn(
        "h-auto rounded-sm bg-transparent px-1.5 py-1 font-mono text-[0.7rem] tracking-wide uppercase",
        tone[badge],
        className,
      )}
    >
      <span className="text-sm font-medium tabular-nums normal-case">{score}</span>
      {badge}
    </Badge>
  );
}
