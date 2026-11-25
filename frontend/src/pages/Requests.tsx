import { Fragment, useEffect, useState } from "react";
import { api } from "../api";

type Row = {
  id: number; created_at: string; name: string; email: string; company_name: string;
  job_title: string | null; sector: string | null; company_size: string | null;
  need: string | null; message: string | null; notification_sent: boolean;
};

export default function Requests() {
  const [rows, setRows] = useState<Row[]>([]);
  const [err, setErr] = useState("");
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState<number | null>(null);
  useEffect(() => {
    api<Row[]>("/demo-requests/").then(setRows).catch((e) => setErr(e.message)).finally(() => setLoading(false));
  }, []);
  return (
    <>
      <h2>Solicitudes de demostración</h2>
      <p className="mut">Personas que completaron el formulario de la landing. Se eliminan automáticamente a los 7 días: antes de ese plazo, copia las solicitudes calificadas al registro de oportunidades (se conservan allí hasta 12 meses sin actividad, según la política de privacidad).</p>
      {err && <p className="err" role="alert">{err}</p>}
      <div className="card tw">
        {loading ? <span className="mut">Cargando…</span> : rows.length === 0 && !err ? <span className="mut">Aún no hay solicitudes.</span> : (
          <table>
            <thead><tr><th>Fecha</th><th>Nombre</th><th>Empresa</th><th>Cargo</th><th>Sector</th><th>Correo</th><th /></tr></thead>
            <tbody>{rows.map((r) => (
              <Fragment key={r.id}>
                <tr>
                  <td>{new Date(r.created_at).toLocaleString()}</td><td>{r.name}</td><td>{r.company_name}</td>
                  <td>{r.job_title ?? ""}</td><td>{r.sector ?? ""}</td>
                  <td><a href={`mailto:${r.email}`}>{r.email}</a></td>
                  <td><button className="ghost" onClick={() => setOpen(open === r.id ? null : r.id)} aria-expanded={open === r.id}>{open === r.id ? "Ocultar" : "Ver"}</button></td>
                </tr>
                {open === r.id && <tr><td colSpan={7} style={{ whiteSpace: "normal" }}>
                  {r.need && <><b>Necesidad:</b> {r.need}<br /></>}
                  {r.message && <><b>Mensaje:</b> {r.message}<br /></>}
                  {r.company_size && <><b>Tamaño:</b> {r.company_size}<br /></>}
                  <b>Correo de aviso al equipo:</b> {r.notification_sent ? "enviado" : "no enviado"}
                </td></tr>}
              </Fragment>
            ))}</tbody>
          </table>
        )}
      </div>
    </>
  );
}
