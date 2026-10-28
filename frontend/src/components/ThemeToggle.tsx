import { useEffect, useState } from "react";

type Theme = "light" | "dark";
function preferredTheme(): Theme {
  try {
    const saved = localStorage.getItem("consultlens-theme");
    if (saved === "light" || saved === "dark") return saved;
  } catch { /* Restricted storage: default to light. */ }
  return "light";
}

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>(preferredTheme);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    try { localStorage.setItem("consultlens-theme", theme); } catch { /* Browsing without persistence. */ }
  }, [theme]);
  return <button type="button" className="theme-toggle" aria-label={`Switch to ${theme === "light" ? "dark" : "light"} theme`}
    title={`Switch to ${theme === "light" ? "dark" : "light"} theme`}
    onClick={() => setTheme(t => t === "light" ? "dark" : "light")}>
    <span aria-hidden="true">{theme === "light" ? "☾" : "☀"}</span>
    <span>{theme === "light" ? "Dark mode" : "Light mode"}</span>
  </button>;
}
