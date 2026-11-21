import { FormEvent, useState } from "react";
import { api } from "../api";

export default function Account() {
  const [msg, setMsg] = useState<{ ok: boolean; text: string } | null>(null);
  const submit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const d = Object.fromEntries(new FormData(form)) as Record<string, string>;
    if (d.new_password !== d.confirm) { setMsg({ ok: false, text: "La confirmación no coincide." }); return; }
    try {
      await api("/account/password", "POST", { current_password: d.current_password, new_password: d.new_password });
      form.reset(); setMsg({ ok: true, text: "Contraseña actualizada." });
    } catch (x: any) { setMsg({ ok: false, text: x.message }); }
  };
  return (
    <>
      <h2>Cuenta</h2>
      <form className="card" style={{ maxWidth: 420 }} onSubmit={submit}>
        <b>Cambiar contraseña</b>
        <label>Contraseña actual</label><input name="current_password" type="password" required autoComplete="current-password" />
        <label>Nueva contraseña (mínimo 12 caracteres)</label><input name="new_password" type="password" required minLength={12} maxLength={72} autoComplete="new-password" />
        <label>Confirmar nueva contraseña</label><input name="confirm" type="password" required minLength={12} autoComplete="new-password" />
        {msg && <p className={msg.ok ? "mut" : "err"}>{msg.text}</p>}
        <br /><button>Guardar</button>
      </form>
    </>
  );
}
