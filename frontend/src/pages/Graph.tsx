import { FormEvent, useCallback, useEffect, useMemo, useState } from "react";
import { api, companyId } from "../api";

type Ref = { type: string; id: number };
type GNode = Ref & { name?: string; sku?: string };
type Rel = { id: number; source: Ref; relationship: string; target: Ref };
type G = { entity: Ref; nodes: GNode[]; relationships: Rel[] };

// Colores de entidad del sistema de diseño (tokens.css): cambian con el tema.
const COLORS: Record<string, string> = { company: "var(--entity-company)", customer: "var(--entity-customer)", product: "var(--entity-product)", warehouse: "var(--entity-warehouse)" };
const TYPES: [string, string][] = [["company", "Empresa"], ["customer", "Cliente"], ["product", "Producto"], ["warehouse", "Bodega"]];
const key = (r: Ref) => `${r.type}:${r.id}`;
const label = (n: GNode) => { const t = n.name ?? n.sku ?? `${n.type} #${n.id}`; return t.length > 18 ? t.slice(0, 17) + "…" : t; };

export default function Graph() {
  const [type, setType] = useState("company");
  const [id, setId] = useState(companyId() ?? 1);
  const [depth, setDepth] = useState(1);
  const [data, setData] = useState<G | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  const go = useCallback((t: string, i: number, d: number) => {
    setLoading(true); setErr("");
    api<G>(`/graph/entity/${t}/${i}?depth=${d}`).then(setData).catch((e) => { setData(null); setErr(e.message); }).finally(() => setLoading(false));
  }, []);
  useEffect(() => { go("company", id, 1); /* carga inicial */ // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const submit = (e: FormEvent) => { e.preventDefault(); go(type, id, depth); };
  const pick = (n: Ref) => { setType(n.type); setId(n.id); go(n.type, n.id, depth); };

  const view = useMemo(() => {
    if (!data) return null;
    const nodes = [...new Map(data.nodes.map((n) => [key(n), n])).values()]; // sin duplicados
    const known = new Set(nodes.map(key));
    const edges = data.relationships.filter((r) => known.has(key(r.source)) && known.has(key(r.target)));
    const ring = new Map<string, number>([[key(data.entity), 0]]);
    for (let q = [key(data.entity)]; q.length; ) {
      const cur = q.shift()!;
      edges.forEach((r) => {
        const a = key(r.source), b = key(r.target);
        const nx = a === cur ? b : b === cur ? a : null;
        if (nx && !ring.has(nx)) { ring.set(nx, ring.get(cur)! + 1); q.push(nx); }
      });
    }
    const maxR = Math.max(1, ...ring.values());
    const groups = new Map<number, GNode[]>();
    nodes.forEach((n) => { const r = ring.get(key(n)) ?? maxR + 1; groups.set(r, [...(groups.get(r) ?? []), n]); });
    const pos = new Map<string, { x: number; y: number }>();
    groups.forEach((list, r) => list.forEach((n, i) => {
      const ang = (2 * Math.PI * i) / list.length - Math.PI / 2;
      pos.set(key(n), r === 0 ? { x: 0, y: 0 } : { x: Math.cos(ang) * 140 * r, y: Math.sin(ang) * 140 * r });
    }));
    return { nodes, edges, pos, S: 140 * Math.max(...groups.keys(), 1) + 70, hidden: data.relationships.length - edges.length };
  }, [data]);

  return (
    <>
      <h2>Grafo de relaciones</h2>
      <p className="mut">Explora cómo se conectan las entidades de tu empresa. Haz clic en un nodo para centrar el grafo en él.</p>
      <form className="card grid" onSubmit={submit}>
        <div><label htmlFor="gt">Entidad</label><select id="gt" value={type} onChange={(e) => setType(e.target.value)}>{TYPES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}</select></div>
        <div><label htmlFor="gi">ID</label><input id="gi" type="number" min={1} value={id} onChange={(e) => setId(Number(e.target.value))} required /></div>
        <div><label htmlFor="gd">Profundidad</label><select id="gd" value={depth} onChange={(e) => setDepth(Number(e.target.value))}>{[1, 2, 3].map((d) => <option key={d}>{d}</option>)}</select></div>
        <button disabled={loading}>{loading ? "Cargando…" : "Ver grafo"}</button>
      </form>
      {err && <p className="err" role="alert">{err}</p>}
      {view && view.nodes.length === 0 && <div className="card mut">No se encontró esa entidad en tu empresa.</div>}
      {view && view.nodes.length > 0 && (
        <div className="card">
          <svg className="gsvg" viewBox={`${-view.S} ${-view.S} ${2 * view.S} ${2 * view.S}`} role="img" aria-label={`Grafo con ${view.nodes.length} nodos y ${view.edges.length} relaciones`}>
            {view.edges.map((r) => { const a = view.pos.get(key(r.source))!, b = view.pos.get(key(r.target))!; return (
              <g key={r.id}><line x1={a.x} y1={a.y} x2={b.x} y2={b.y} style={{ stroke: "var(--blue)" }} strokeOpacity=".5" strokeWidth="1.5"><title>{r.relationship}</title></line>
                <text x={(a.x + b.x) / 2} y={(a.y + b.y) / 2} fontSize="10" style={{ fill: "var(--text-muted-app)" }} textAnchor="middle">{r.relationship}</text></g>); })}
            {view.nodes.map((n) => { const p = view.pos.get(key(n))!; return (
              <g key={key(n)} className="n" tabIndex={0} role="button" aria-label={`${n.type} ${label(n)}`} transform={`translate(${p.x} ${p.y})`}
                onClick={() => pick(n)} onKeyDown={(e) => e.key === "Enter" && pick(n)}>
                <circle r="20" style={{ fill: COLORS[n.type] ?? "var(--text-muted-app)" }} /><text y="38" fontSize="12" style={{ fill: "var(--text)" }} textAnchor="middle">{label(n)}</text></g>); })}
          </svg>
          <div className="legend">{TYPES.map(([v, l]) => <span key={v}><i style={{ background: COLORS[v] }} />{l}</span>)}</div>
          {view.hidden > 0 && <p className="mut">{view.hidden} relación(es) apuntan a entidades que esta vista aún no puede mostrar.</p>}
        </div>
      )}
    </>
  );
}
