import { Fragment, useEffect, useState } from "react";
import { api } from "../api";

type Row = { id: number; created_at: string; full_name: string; email: string; company: string; job_title: string; sector: string; company_size: string | null; need: string; message: string | null };

export default function Contacts() {
  const [rows, setRows] = useState<Row[]>([]);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState<number | null>(null);
  useEffect(() => {
    api<Row[]>("/contact/requests").then(setRows).catch((e) => setErr(e.message)).finally(() => setLoading(false));
  }, []);
  return (
    <>
      <h2>Solicitudes de contacto</h2>
      <p className="mut">Personas que completaron el formulario de la landing. Se eliminan automáticamente a los 7 días: exporta o gestiona cada contacto antes de ese plazo.</p>
      {err && <p className="err" role="alert">{err}</p>}
      <div className="card tw">
        {loading ? <span className="mut">Cargando…</span> : rows.length === 0 && !err ? <span className="mut">Aún no hay solicitudes.</span> : (
          <table>
            <thead><tr><th>Fecha</th><th>Nombre</th><th>Empresa</th><th>Cargo</th><th>Sector</th><th>Correo</th><th /></tr></thead>
            <tbody>{rows.map((r) => (
              <Fragment key={r.id}>
                <tr>
                  <td>{new Date(r.created_at).toLocaleString()}</td><td>{r.full_name}</td><td>{r.company}</td><td>{r.job_title}</td><td>{r.sector}</td>
                  <td><a href={`mailto:${r.email}`}>{r.email}</a></td>
                  <td><button className="ghost" onClick={() => setOpen(open === r.id ? null : r.id)} aria-expanded={open === r.id}>{open === r.id ? "Ocultar" : "Ver"}</button></td>
                </tr>
                {open === r.id && <tr><td colSpan={7} style={{ whiteSpace: "normal" }}>
                  <b>Necesidad:</b> {r.need}{r.message && <><br /><b>Mensaje:</b> {r.message}</>}{r.company_size && <><br /><b>Tamaño:</b> {r.company_size}</>}
                </td></tr>}
              </Fragment>
            ))}</tbody>
          </table>
        )}
      </div>
    </>
  );
}
