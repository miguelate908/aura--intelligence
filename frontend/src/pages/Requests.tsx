import { Fragment, useEffect, useState } from "react";
import { api } from "../api";
import { SITE } from "../siteConfig";

type Row = {
  id: number; created_at: string | null; name: string; email: string; company_name: string;
  job_title: string | null; sector: string | null; company_size: string | null;
  need: string | null; message: string | null; notification_sent: boolean;
};

const policyCutoff = Date.parse(SITE.privacyPolicyUpdatedAt);

function RequestDate({ value }: { value: Row["created_at"] }) {
  // Solo las fechas con zona explícita identifican el mismo instante en todos los navegadores.
  const match = value?.match(/^(\d{4}-\d{2}-\d{2})T(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/);
  const instant = match && value ? Date.parse(value) : NaN;
  const day = match && new Date(match[1] + "T00:00:00Z");
  if (!Number.isFinite(instant) || !day || !Number.isFinite(day.getTime()) || day.toISOString().slice(0, 10) !== match[1]) {
    return <>Fecha sin verificar<br /><span className="badge-warn">Revisar autorización</span></>;
  }
  return <>{new Date(instant).toLocaleString()}{instant < policyCutoff && <><br /><span className="badge-warn">Pedir autorización</span></>}</>;
}

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
      <p className="mut">Las solicitudes se eliminan del panel a los 7 días. Antes de copiar una solicitud calificada al registro de oportunidades, revisa su autorización.</p>
      <section className="card notice" aria-labelledby="notice-mail">
        <h3 id="notice-mail">Correo de aviso al equipo</h3>
        <ul>
          <li>Si se envió el correo de aviso, úsalo solo para atender la solicitud y bórralo de tu bandeja cuando termines.</li>
          <li><b>Pedir autorización</b> indica que la solicitud llegó antes del cambio de política. Sigue el kit de ventas (§9) y espera una respuesta afirmativa antes de copiarla al registro.</li>
          <li><b>Revisar autorización</b> indica que la fecha es incierta. Comprueba la autorización antes de copiar los datos.</li>
          <li>Si alguien pide que borremos sus datos, bórralos también del correo y del registro de oportunidades.</li>
        </ul>
      </section>
      {err && <p className="err" role="alert">{err}</p>}
      <div className="card tw">
        {loading ? <span className="mut">Cargando…</span> : rows.length === 0 && !err ? <span className="mut">Aún no hay solicitudes.</span> : (
          <table>
            <thead><tr><th>Fecha</th><th>Nombre</th><th>Empresa</th><th>Cargo</th><th>Sector</th><th>Correo</th><th /></tr></thead>
            <tbody>{rows.map((r) => (
              <Fragment key={r.id}>
                <tr>
                  <td><RequestDate value={r.created_at} /></td><td>{r.name}</td><td>{r.company_name}</td>
                  <td>{r.job_title ?? ""}</td><td>{r.sector ?? ""}</td>
                  <td><a href={`mailto:${r.email}`}>{r.email}</a></td>
                  <td><button className="ghost" onClick={() => setOpen(open === r.id ? null : r.id)} aria-expanded={open === r.id}>{open === r.id ? "Ocultar" : "Ver"}</button></td>
                </tr>
                {open === r.id && <tr><td colSpan={7} style={{ whiteSpace: "normal" }}>
                  {r.need && <><b>Necesidad:</b> {r.need}<br /></>}
                  {r.message && <><b>Mensaje:</b> {r.message}<br /></>}
                  {r.company_size && <><b>Tamaño:</b> {r.company_size}<br /></>}
                  <b>Correo de aviso al equipo:</b> {r.notification_sent ? "enviado. Bórralo de tu bandeja cuando termines de atender esta solicitud." : "no enviado"}
                </td></tr>}
              </Fragment>
            ))}</tbody>
          </table>
        )}
      </div>
    </>
  );
}
