import { FormEvent, useCallback, useEffect, useState } from "react";
import { api, companyId } from "../api";
import { normalize, parseCsv } from "../csv";

type Field = { name: string; label: string; type: string; required: boolean };
const PAGE = 10;

// "29.500" o "1.250,75" (formato colombiano) y "1,250.75" pasan a número con punto decimal.
function toNumber(v: string): string {
  const t = v.replace(/[\s$]/g, "");
  if (/^\d{1,3}(\.\d{3})+(,\d+)?$/.test(t)) return t.replace(/\./g, "").replace(",", ".");
  if (/^\d{1,3}(,\d{3})+(\.\d+)?$/.test(t)) return t.replace(/,/g, "");
  return t.replace(",", ".");
}

type ImportError = { row: number; error: string };

export default function Resource({ path, title, fields }: { path: string; title: string; fields: Field[] }) {
  const [rows, setRows] = useState<any[]>([]);
  const [err, setErr] = useState("");
  const [ok, setOk] = useState("");
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState("");
  const [page, setPage] = useState(0);
  const [importing, setImporting] = useState(false);
  const [importErrors, setImportErrors] = useState<ImportError[]>([]);
  const [editing, setEditing] = useState<number | null>(null);
  const [draft, setDraft] = useState<Record<string, string>>({});
  const [busy, setBusy] = useState(false);
  const load = useCallback(() => {
    setLoading(true);
    return api<any[]>(path).then(setRows).catch((e) => setErr(e.message)).finally(() => setLoading(false));
  }, [path]);
  useEffect(() => { setRows([]); setErr(""); setOk(""); setImportErrors([]); setQ(""); setPage(0); setEditing(null); load(); }, [load]);

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

  const importCsv = async (file: File) => {
    setErr(""); setOk(""); setImportErrors([]);
    const table = parseCsv(await file.text());
    if (table.length < 2) { setErr("El archivo no tiene filas de datos."); return; }
    const byHeader: Record<string, string> = {};
    fields.forEach((f) => { byHeader[normalize(f.name)] = f.name; byHeader[normalize(f.label)] = f.name; });
    const cols = table[0].map((h) => byHeader[normalize(h)]);
    const missing = fields.filter((f) => f.required && !cols.includes(f.name)).map((f) => f.label);
    if (missing.length) { setErr(`Faltan columnas obligatorias: ${missing.join(", ")}.`); return; }
    const rows = table.slice(1).map((cells) => {
      const row: Record<string, string> = {};
      cols.forEach((name, i) => {
        if (!name) return;
        const v = (cells[i] ?? "").trim();
        row[name] = fields.find((f) => f.name === name)?.type === "number" && v ? toNumber(v) : v;
      });
      return row;
    });
    setImporting(true);
    try {
      const r = await api<{ imported: number }>(`/import${path}`, "POST", { rows });
      setOk(`Se importaron ${r.imported} registro(s).`);
      load();
    } catch (x: any) {
      setErr(x.message);
      setImportErrors(x.detail?.errors ?? []);
    } finally {
      setImporting(false);
    }
  };
  const startEdit = (r: any) => {
    setEditing(r.id);
    setDraft(Object.fromEntries(fields.map((f) => [f.name, r[f.name] == null ? "" : String(r[f.name])])));
  };
  const saveEdit = async (id: number) => {
    const body: Record<string, unknown> = {};
    for (const f of fields) {
      const v = (draft[f.name] ?? "").trim();
      if (f.required && !v) { setOk(""); setErr(`El campo ${f.label} es obligatorio.`); return; }
      body[f.name] = v === "" ? (f.type === "number" ? 0 : null) : f.type === "number" ? Number(toNumber(v)) : v;
    }
    setBusy(true);
    try { await api(`${path}/${id}`, "PUT", body); setEditing(null); setErr(""); setOk("Registro actualizado."); await load(); }
    catch (x: any) { setOk(""); setErr(x.message); }
    finally { setBusy(false); }
  };
  const remove = async (r: any) => {
    if (!window.confirm(`¿Eliminar “${r.name ?? r.id}”? Esta acción no se puede deshacer.`)) return;
    setBusy(true);
    try { await api(`${path}/${r.id}`, "DELETE"); setErr(""); setOk("Registro eliminado."); await load(); }
    catch (x: any) { setOk(""); setErr(x.message); }
    finally { setBusy(false); }
  };
  const template = `data:text/csv;charset=utf-8,${encodeURIComponent(fields.map((f) => f.label).join(";") + "\r\n")}`;

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
      <div className="card import">
        <label htmlFor={`csv-${path}`}>Importar desde CSV</label>
        <input id={`csv-${path}`} type="file" accept=".csv,text/csv" disabled={importing}
          onChange={(e) => { const f = e.target.files?.[0]; e.target.value = ""; if (f) importCsv(f); }} />
        <span className="mut">
          {importing ? "Importando…" : <>Columnas: {fields.map((f) => f.label).join(", ")}. Si una fila tiene errores no se importa ninguna. <a href={template} download={`plantilla-${path.slice(1)}.csv`}>Descargar plantilla</a></>}
        </span>
      </div>
      {err && <p className="err" role="alert">{err}</p>}
      {importErrors.length > 0 && (
        <ul className="err">{importErrors.map((e) => <li key={e.row}>Fila {e.row + 1} del archivo: {e.error}</li>)}</ul>
      )}
      {ok && <p className="ok" role="status">{ok}</p>}
      <div className="card tw">
        <div className="bar">
          <span className="mut">{filtered.length} registro{filtered.length === 1 ? "" : "s"}</span>
          <input type="search" aria-label="Buscar" placeholder="Buscar…" value={q} onChange={(e) => { setQ(e.target.value); setPage(0); }} />
        </div>
        {loading ? <span className="mut">Cargando…</span> : rows.length === 0 ? <span className="mut">Todavía no hay registros.</span> : filtered.length === 0 ? <span className="mut">Sin resultados para “{q}”.</span> : (
          <table>
            <thead><tr>{cols.map((c) => <th key={c}>{labels[c] ?? c}</th>)}<th>Acciones</th></tr></thead>
            <tbody>{view.map((r) => editing === r.id ? (
              <tr key={r.id}>
                {cols.map((c) => {
                  const f = fields.find((x) => x.name === c);
                  return <td key={c}>{f ? (
                    <input aria-label={f.label} type={f.type === "number" ? "text" : f.type} inputMode={f.type === "number" ? "decimal" : undefined}
                      value={draft[c] ?? ""} onChange={(e) => setDraft({ ...draft, [c]: e.target.value })}
                      onKeyDown={(e) => { if (e.key === "Enter") saveEdit(r.id); if (e.key === "Escape") setEditing(null); }} />
                  ) : cell(c, r[c])}</td>;
                })}
                <td className="actions">
                  <button disabled={busy} onClick={() => saveEdit(r.id)}>Guardar</button>
                  <button className="ghost" disabled={busy} onClick={() => setEditing(null)}>Cancelar</button>
                </td>
              </tr>
            ) : (
              <tr key={r.id}>
                {cols.map((c) => <td key={c}>{cell(c, r[c])}</td>)}
                <td className="actions">
                  <button className="ghost" disabled={busy || editing !== null} onClick={() => startEdit(r)}>Editar</button>
                  <button className="ghost danger" disabled={busy || editing !== null} onClick={() => remove(r)}>Eliminar</button>
                </td>
              </tr>
            ))}</tbody>
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
