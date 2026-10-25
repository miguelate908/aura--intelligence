import { FormEvent, useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../auth";

export default function Login() {
  const { authed, login, register } = useAuth();
  const [reg, setReg] = useState(false);
  const [f, setF] = useState({ company: "", name: "", email: "", password: "" });
  const [err, setErr] = useState("");
  if (authed) return <Navigate to="/" replace />;
  const set = (k: string) => (e: any) => setF({ ...f, [k]: e.target.value });
  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setErr("");
    try { reg ? await register(f.company, f.name, f.email, f.password) : await login(f.email, f.password); }
    catch (x: any) { setErr(x.message); }
  };
  return (
    <form className="card auth" onSubmit={submit}>
      <h1>AURA Intelligence</h1>
      {reg && <><label>Empresa</label><input value={f.company} onChange={set("company")} required /><label>Tu nombre</label><input value={f.name} onChange={set("name")} required /></>}
      <label>Correo</label><input type="email" value={f.email} onChange={set("email")} required />
      <label>Contraseña {reg && "(mínimo 12 caracteres)"}</label><input type="password" value={f.password} onChange={set("password")} required />
      {err && <p className="err">{err}</p>}
      <button>{reg ? "Crear empresa" : "Ingresar"}</button>
      <button type="button" className="ghost" onClick={() => setReg(!reg)}>{reg ? "Ya tengo cuenta" : "Crear empresa nueva"}</button>
    </form>
  );
}
