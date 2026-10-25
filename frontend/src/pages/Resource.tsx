import { FormEvent, useCallback, useEffect, useState } from "react";
import { api, companyId } from "../api";

type Field = { name: string; label: string; type: string; required: boolean };

export default function Resource({ path, title, fields }: { path: string; title: string; fields: Field[] }) {
  const [rows, setRows] = useState<any[]>([]);
  const [err, setErr] = useState("");
  const load = useCallback(() => api<any[]>(path).then(setRows).catch((e) => setErr(e.message)), [path]);
  useEffect(() => { setRows([]); setErr(""); load(); }, [load]);

  const submit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const body: Record<string, unknown> = { company_id: companyId() };
    new FormData(e.currentTarget).forEach((v, k) => {
      if (v !== "") body[k] = fields.find((f) => f.name === k)?.type === "number" ? Number(v) : v;
    });
    try { await api(path, "POST", body); e.currentTarget.reset(); setErr(""); load(); }
    catch (x: any) { setErr(x.message); }
  };

  const cols = rows[0] ? Object.keys(rows[0]) : [];
  return (
    <>
      <h2>{title}</h2>
      <form className="card grid" onSubmit={submit}>
        {fields.map((f) => (
          <div key={f.name}><label>{f.label}</label><input name={f.name} type={f.type} step="any" required={f.required} /></div>
        ))}
        <button>Agregar</button>
      </form>
      {err && <p className="err">{err}</p>}
      <div className="card tw">
        {rows.length === 0 ? <span className="mut">Todavía no hay registros.</span> : (
          <table>
            <thead><tr>{cols.map((c) => <th key={c}>{c}</th>)}</tr></thead>
            <tbody>{rows.map((r) => <tr key={r.id}>{cols.map((c) => <td key={c}>{String(r[c] ?? "")}</td>)}</tr>)}</tbody>
          </table>
        )}
      </div>
    </>
  );
}
