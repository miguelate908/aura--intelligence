import { FormEvent, useState } from "react";
import { Link, Navigate } from "react-router-dom";
import { useAuth } from "../auth";
import EdithMark from "../assets/edith-mark.svg";

export default function Login() {
  const { authed, login, register } = useAuth();
  const [reg, setReg] = useState(false);
  const [f, setF] = useState({ company: "", name: "", email: "", password: "" });
  const [err, setErr] = useState("");
  const [busy, setBusy] = useState(false);
  if (authed) return <Navigate to="/app" replace />;
  const set = (k: string) => (e: any) => setF({ ...f, [k]: e.target.value });
  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setErr(""); setBusy(true);
    try { reg ? await register(f.company, f.name, f.email, f.password) : await login(f.email, f.password); }
    catch (x: any) { setErr(x.message); }
    finally { setBusy(false); }
  };
  return (
    <div className="panel"><div className="authwrap">
      <form className="card auth" onSubmit={submit}>
        <h1 className="auth-brand"><img src={EdithMark} alt="" aria-hidden="true" />EDITH Intelligence</h1>
        <p className="mut">{reg ? "Crea tu empresa y tu primer usuario." : "Accede a tu panel."}</p>
        {reg && <>
          <label htmlFor="co">Empresa</label><input id="co" value={f.company} onChange={set("company")} required autoComplete="organization" />
          <label htmlFor="nm">Tu nombre</label><input id="nm" value={f.name} onChange={set("name")} required autoComplete="name" />
        </>}
        <label htmlFor="em">Correo</label><input id="em" type="email" value={f.email} onChange={set("email")} required autoComplete="email" />
        <label htmlFor="pw">Contraseña {reg && "(mínimo 12 caracteres)"}</label>
        <input id="pw" type="password" value={f.password} onChange={set("password")} required minLength={reg ? 12 : undefined} autoComplete={reg ? "new-password" : "current-password"} />
        {err && <p className="err" role="alert">{err}</p>}
        <button disabled={busy}>{busy ? "Un momento…" : reg ? "Crear empresa" : "Ingresar"}</button>
        <button type="button" className="ghost" onClick={() => { setReg(!reg); setErr(""); }}>{reg ? "Ya tengo cuenta" : "Crear empresa nueva"}</button>
        <Link className="back" to="/">← Volver al inicio</Link>
      </form>
    </div></div>
  );
}
