const KEY = "aura_token";
export const getToken = () => localStorage.getItem(KEY);
export const setToken = (t: string | null) => (t ? localStorage.setItem(KEY, t) : localStorage.removeItem(KEY));

export function companyId(): number | null {
  const t = getToken();
  if (!t) return null;
  try {
    return JSON.parse(atob(t.split(".")[1].replace(/-/g, "+").replace(/_/g, "/"))).company_id ?? null;
  } catch {
    return null;
  }
}

export async function api<T = any>(path: string, method = "GET", body?: unknown): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  const t = getToken();
  if (t) headers.Authorization = `Bearer ${t}`;
  const apiPrefix = import.meta.env.DEV ? "/api" : "";
  const r = await fetch(`${apiPrefix}${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined });
  const text = await r.text();
  let d: any;
  try { d = JSON.parse(text); } catch { d = text; }
  if (r.status === 401 && t) { setToken(null); location.href = "/login"; }
  if (!r.ok) {
    const m = d?.detail;
    if (m && typeof m === "object" && !Array.isArray(m)) {
      // Errores con estructura (p. ej. importación: { message, errors }).
      throw Object.assign(new Error(m.message || `Error ${r.status}`), { detail: m });
    }
    throw new Error(Array.isArray(m) ? m.map((x: any) => x.msg).join("; ") : m || `Error ${r.status}`);
  }
  return d as T;
}
