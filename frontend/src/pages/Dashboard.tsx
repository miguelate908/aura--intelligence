import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

const ITEMS: [string, string][] = [["/customers", "Clientes"], ["/products", "Productos"], ["/warehouses", "Bodegas"], ["/events", "Eventos"]];

export default function Dashboard() {
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [inv, setInv] = useState<any[] | null>(null);
  useEffect(() => {
    ITEMS.forEach(([p]) => api<any[]>(p).then((d) => setCounts((c) => ({ ...c, [p]: d.length }))).catch(() => {}));
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
