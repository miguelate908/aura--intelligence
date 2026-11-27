import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

const ITEMS: [string, string][] = [["customers", "Clientes"], ["products", "Productos"], ["warehouses", "Bodegas"], ["events", "Eventos"]];

type Summary = {
  counts: Record<string, number>;
  recent_events: { event_type: string; description: string | null; created_at: string }[];
};

export default function Dashboard() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [inv, setInv] = useState<any[] | null>(null);
  const counts = summary?.counts ?? {};
  useEffect(() => {
    // Una sola petición: los conteos se calculan en la base, sin descargar todos los registros.
    api<Summary>("/summary/").then(setSummary).catch(() => {});
    // Si el módulo de inventario no está desplegado, se ocultan sus tarjetas.
    api<any[]>("/inventory").then(setInv).catch(() => setInv(null));
  }, []);
  const units = (inv ?? []).reduce((s, r) => s + r.quantity, 0);
  const low = (inv ?? []).filter((r) => r.quantity <= r.minimum_quantity);
  return (
    <>
      <h2>Resumen</h2>
      <div className="grid">
        {ITEMS.map(([p, l]) => (
          <div className="card" key={p}><div className="mut">{l}</div><div className="kpi">{counts[p] ?? "–"}</div></div>
        ))}
        {inv && <div className="card"><div className="mut">Unidades en inventario</div><div className="kpi">{units}</div></div>}
        {inv && <div className="card"><div className="mut">Con stock bajo</div><div className="kpi" style={low.length ? { color: "var(--err)" } : undefined}>{low.length}</div></div>}
      </div>
      {summary && summary.recent_events.length > 0 && (
        <div className="card">
          <b>Actividad reciente</b>
          <ul>{summary.recent_events.map((e, i) => (
            <li key={i}>{e.description || e.event_type} <span className="mut">· {new Date(e.created_at).toLocaleString("es-CO")}</span></li>
          ))}</ul>
        </div>
      )}
      {low.length > 0 && (
        <div className="card">
          <b>Por reponer</b>
          <ul>{low.slice(0, 8).map((r) => <li key={r.id}>{r.product_name} en {r.warehouse_name}: {r.quantity} (mínimo {r.minimum_quantity})</li>)}</ul>
          <Link to="/app/inventory">Ir al inventario →</Link>
        </div>
      )}
      {inv && inv.length === 0 && <div className="card mut">Aún no hay inventario. Crea productos y bodegas, y agrégalos en <Link to="/app/inventory">Inventario</Link>.</div>}
    </>
  );
}
