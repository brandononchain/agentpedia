import type { BadgeName } from "@/lib/catalog";

export function ScoreMark({ score, badge }: { score: number; badge: BadgeName; className?: string }) {
  const label = badge === "clean" ? "clean" : badge === "noted" ? "noted" : "blocked";
  return (
    <span className={`score-mark score-${badge}`}>
      <span className="score-num">{score}</span>
      <span>{label}</span>
    </span>
  );
}
