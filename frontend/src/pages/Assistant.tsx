import { FormEvent, useState } from "react";
import { api } from "../api";

type Msg = { who: "me" | "bot"; text: string };

export default function Assistant() {
  const [log, setLog] = useState<Msg[]>([{ who: "bot", text: "Hola, soy el asistente de AURA. ¿Qué necesitas?" }]);
  const [q, setQ] = useState("");
  const [busy, setBusy] = useState(false);
  const send = async (e: FormEvent) => {
    e.preventDefault();
    const text = q.trim();
    if (!text || busy) return;
    setQ(""); setBusy(true);
    setLog((l) => [...l, { who: "me", text }]);
    try {
      const d = await api<{ reply: string }>("/assistant/chat", "POST", { message: text });
      setLog((l) => [...l, { who: "bot", text: d.reply }]);
    } catch (x: any) {
      setLog((l) => [...l, { who: "bot", text: "No pude responder: " + x.message }]);
    } finally { setBusy(false); }
  };
  return (
    <>
      <h2>Asistente IA</h2>
      <div className="card">
        <div className="log">{log.map((m, i) => <div key={i} className={`msg ${m.who}`}>{m.text}</div>)}{busy && <div className="msg bot">Pensando…</div>}</div>
        <form className="row" onSubmit={send}><input value={q} onChange={(e) => setQ(e.target.value)} placeholder="Escribe tu pregunta…" /><button>Enviar</button></form>
      </div>
    </>
  );
}
