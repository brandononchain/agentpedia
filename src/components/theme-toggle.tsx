"use client";

import { useEffect, useState } from "react";

const KEY = "encyclopedia-theme";

export function ThemeToggle() {
  const [dark, setDark] = useState<boolean | null>(null);

  useEffect(() => {
    setDark(document.documentElement.classList.contains("dark"));
  }, []);

  function toggle() {
    const next = !document.documentElement.classList.contains("dark");
    document.documentElement.classList.toggle("dark", next);
    localStorage.setItem(KEY, next ? "dark" : "light");
    setDark(next);
  }

  return (
    <button type="button" className="theme-toggle" aria-pressed={dark === true} onClick={toggle}>
      {dark === null ? "Paper" : dark ? "Light paper" : "Dark paper"}
    </button>
  );
}
