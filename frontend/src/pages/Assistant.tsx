import { FormEvent, useEffect, useRef, useState } from "react";
import { api } from "../api";

type Msg = { who: "me" | "bot"; text: string };

export default function Assistant() {
  const [log, setLog] = useState<Msg[]>([{ who: "bot", text: "Hola, soy EDITH, tu asistente inteligente. ¿Qué necesitas?" }]);
  const [q, setQ] = useState("");
  const [busy, setBusy] = useState(false);
  const end = useRef<HTMLDivElement>(null);
  useEffect(() => { end.current?.scrollIntoView({ block: "end" }); }, [log, busy]);
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
        <div className="log" role="log" aria-live="polite">
          {log.map((m, i) => <div key={i} className={`msg ${m.who}`}>{m.text}</div>)}
          {busy && <div className="msg bot">Pensando…</div>}
          <div ref={end} />
        </div>
        <form className="row" onSubmit={send}>
          <input aria-label="Tu pregunta" value={q} onChange={(e) => setQ(e.target.value)} placeholder="Escribe tu pregunta…" />
          <button disabled={busy || !q.trim()}>Enviar</button>
        </form>
      </div>
    </>
  );
}
