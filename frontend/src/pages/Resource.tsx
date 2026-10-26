import { FormEvent, useCallback, useEffect, useState } from "react";
import { api, companyId } from "../api";

type Field = { name: string; label: string; type: string; required: boolean };
const PAGE = 10;

export default function Resource({ path, title, fields }: { path: string; title: string; fields: Field[] }) {
  const [rows, setRows] = useState<any[]>([]);
  const [err, setErr] = useState("");
  const [ok, setOk] = useState("");
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [page, setPage] = useState(0);
  const load = useCallback(() => {
    setLoading(true);
    return api<any[]>(path).then(setRows).catch((e) => setErr(e.message)).finally(() => setLoading(false));
  }, [path]);
  useEffect(() => { setRows([]); setErr(""); setOk(""); setQ(""); setPage(0); load(); }, [load]);

  const submit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget; // se guarda antes del await: después de él currentTarget es null
    const body: Record<string, unknown> = { company_id: companyId() };
    new FormData(form).forEach((v, k) => {
      if (v !== "") body[k] = fields.find((f) => f.name === k)?.type === "number" ? Number(v) : v;
    });
    try { await api(path, "POST", body); form.reset(); setErr(""); setOk("Registro agregado."); load(); }
    catch (x: any) { setOk(""); setErr(x.message); }
  };

  const labels: Record<string, string> = Object.fromEntries(fields.map((f) => [f.name, f.label]));
  const cols = rows[0] ? Object.keys(rows[0]).filter((c) => c !== "company_id") : [];
  const needle = q.trim().toLowerCase();
  const filtered = needle ? rows.filter((r) => Object.values(r).join(" ").toLowerCase().includes(needle)) : rows;
  const pages = Math.max(1, Math.ceil(filtered.length / PAGE));
  const cur = Math.min(page, pages - 1);
  const view = filtered.slice(cur * PAGE, cur * PAGE + PAGE);
  const cell = (c: string, v: unknown) => (c === "created_at" && v ? new Date(String(v)).toLocaleString() : String(v ?? ""));

  return (
    <>
      <h2>{title}</h2>
      <form className="card grid" onSubmit={submit}>
        {fields.map((f) => (
          <div key={f.name}><label htmlFor={`f-${f.name}`}>{f.label}</label><input id={`f-${f.name}`} name={f.name} type={f.type} step="any" required={f.required} /></div>
        ))}
        <button>Agregar</button>
      </form>
      {err && <p className="err" role="alert">{err}</p>}
      {ok && <p className="ok" role="status">{ok}</p>}
      <div className="card tw">
        <div className="bar">
          <span className="mut">{filtered.length} registro{filtered.length === 1 ? "" : "s"}</span>
          <input type="search" aria-label="Buscar" placeholder="Buscar…" value={q} onChange={(e) => { setQ(e.target.value); setPage(0); }} />
        </div>
        {loading ? <span className="mut">Cargando…</span> : rows.length === 0 ? <span className="mut">Todavía no hay registros.</span> : filtered.length === 0 ? <span className="mut">Sin resultados para “{q}”.</span> : (
          <table>
            <thead><tr>{cols.map((c) => <th key={c}>{labels[c] ?? c}</th>)}</tr></thead>
            <tbody>{view.map((r) => <tr key={r.id}>{cols.map((c) => <td key={c}>{cell(c, r[c])}</td>)}</tr>)}</tbody>
          </table>
        )}
        {pages > 1 && (
          <div className="pager">
            <button className="ghost" disabled={cur === 0} onClick={() => setPage(cur - 1)}>Anterior</button>
            <span className="mut">{cur + 1} / {pages}</span>
            <button className="ghost" disabled={cur >= pages - 1} onClick={() => setPage(cur + 1)}>Siguiente</button>
          </div>
        )}
      </div>
    </>
  );
}
