import { useEffect, useState } from "react";

export type Theme = "dark" | "light";
const KEY = "edith-theme";
// Browser chrome colour per theme (surface-050 in tokens.css)
const CHROME: Record<Theme, string> = { dark: "#070b16", light: "#f8fafc" };

function stored(): Theme {
  try {
    return localStorage.getItem(KEY) === "light" ? "light" : "dark";
  } catch {
    return "dark";
  }
}

function apply(theme: Theme) {
  document.documentElement.dataset.theme = theme;
  document.querySelector('meta[name="theme-color"]')?.setAttribute("content", CHROME[theme]);
}

/** Dark is the default; the choice is remembered per browser. */
export function useTheme() {
  const [theme, setTheme] = useState<Theme>(stored);
  useEffect(() => {
    apply(theme);
    try { localStorage.setItem(KEY, theme); } catch { /* sin almacenamiento: solo esta sesión */ }
  }, [theme]);
  return { theme, toggle: () => setTheme((t) => (t === "dark" ? "light" : "dark")) };
}

export function ThemeToggle({ className = "theme-toggle" }: { className?: string }) {
  const { theme, toggle } = useTheme();
  const next = theme === "dark" ? "claro" : "oscuro";
  return (
    <button type="button" className={className} onClick={toggle} aria-label={`Cambiar a tema ${next}`} title={`Tema ${next}`}>
      <span aria-hidden="true">{theme === "dark" ? "☀" : "☾"}</span>
    </button>
  );
}
