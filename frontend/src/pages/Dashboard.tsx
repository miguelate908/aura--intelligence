import { useEffect, useState } from "react";
import { api } from "../api";

const ITEMS: [string, string][] = [["/customers", "Clientes"], ["/products", "Productos"], ["/warehouses", "Bodegas"], ["/events", "Eventos"]];

export default function Dashboard() {
  const [counts, setCounts] = useState<Record<string, number>>({});
  useEffect(() => {
    ITEMS.forEach(([p]) => api<any[]>(p).then((d) => setCounts((c) => ({ ...c, [p]: d.length }))).catch(() => {}));
  }, []);
  return (
    <>
      <h2>Resumen</h2>
      <div className="grid">
        {ITEMS.map(([p, l]) => (
          <div className="card" key={p}><div className="mut">{l}</div><div className="kpi">{counts[p] ?? "–"}</div></div>
        ))}
      </div>
    </>
  );
}
