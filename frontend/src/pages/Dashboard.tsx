import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

// [ruta API, etiqueta, ruta en el panel (null = sin página aún)]
const ITEMS: [string, string, string | null][] = [
  ["/customers", "Clientes", "/app/customers"],
  ["/products", "Productos", "/app/products"],
  ["/warehouses", "Bodegas", "/app/warehouses"],
  ["/events", "Eventos", null],
];

export default function Dashboard() {
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [failed, setFailed] = useState<Record<string, boolean>>({});
  useEffect(() => {
    ITEMS.forEach(([p]) =>
      api<any[]>(p)
        .then((d) => setCounts((c) => ({ ...c, [p]: d.length })))
        .catch(() => setFailed((f) => ({ ...f, [p]: true })))
    );
  }, []);
  return (
    <>
      <h2>Resumen</h2>
      <p className="mut">Indicadores calculados con los registros reales de tu empresa.</p>
      <div className="grid">
        {ITEMS.map(([p, l, to]) => {
          const body = (<><div className="mut">{l}</div><div className="kpi">{failed[p] ? "—" : counts[p] ?? "…"}</div>{failed[p] && <div className="err">No se pudo cargar</div>}</>);
          return to ? <Link className="card" key={p} to={to}>{body}</Link> : <div className="card" key={p}>{body}</div>;
        })}
      </div>
    </>
  );
}
