import { FormEvent, useState } from "react";
import { api } from "../api";

const capabilities = [
  {
    number: "01",
    title: "Una visión conectada",
    text: "Reúne clientes, productos, bodegas y actividad en un mismo contexto operativo.",
    icon: "◉",
  },
  {
    number: "02",
    title: "Relaciones que se entienden",
    text: "Explora cómo se conectan las entidades de tu empresa y sigue cada vínculo con claridad.",
    icon: "⌘",
  },
  {
    number: "03",
    title: "Preguntas con contexto",
    text: "Consulta la información de tu organización con una experiencia conversacional sencilla.",
    icon: "✳",
  },
];

function BrandMark() {
  return <span className="brand-mark" aria-hidden="true" />;
}

function NetworkIllustration() {
  return (
    <div className="graph-stage" role="img" aria-label="Grafo que conecta la empresa con clientes, productos, almacenes y eventos">
      <svg className="network-svg" viewBox="0 0 620 430" fill="none" aria-hidden="true">
        <defs>
          <linearGradient id="graphLink" x1="100" y1="75" x2="520" y2="360" gradientUnits="userSpaceOnUse"><stop stopColor="#2d7df4" /><stop offset="1" stopColor="#30c8e4" /></linearGradient>
          <linearGradient id="nodeGlow" x1="0" y1="0" x2="1" y2="1"><stop stopColor="#32d6ed" /><stop offset="1" stopColor="#7862f6" /></linearGradient>
          <radialGradient id="graphAura"><stop stopColor="#243d79" stopOpacity=".4" /><stop offset="1" stopColor="#10152a" stopOpacity="0" /></radialGradient>
        </defs>
        <ellipse cx="310" cy="215" rx="275" ry="205" fill="url(#graphAura)" />
        <g stroke="url(#graphLink)" strokeWidth="1.6">
          <path d="M310 218 124 100M310 218 495 106M310 218 104 323M310 218 510 335" />
          <path d="M124 100 495 106M104 323 510 335" strokeDasharray="5 7" opacity=".72" />
        </g>
        <circle cx="124" cy="100" r="27" fill="#20b9d5" fillOpacity=".63" />
        <circle cx="495" cy="106" r="27" fill="#3475e8" fillOpacity=".67" />
        <circle cx="310" cy="218" r="31" fill="#8854e9" fillOpacity=".62" />
        <circle cx="104" cy="323" r="25" fill="#3475e8" fillOpacity=".58" />
        <circle cx="510" cy="335" r="26" fill="#20b9d5" fillOpacity=".61" />
        <g fill="#f1f4fc" fontFamily="Inter, system-ui, sans-serif" fontSize="13" textAnchor="middle">
          <text x="124" y="139">Clientes</text>
          <text x="495" y="145">Productos</text>
          <text x="310" y="223">Empresa</text>
          <text x="104" y="362">Almacenes</text>
          <text x="510" y="374">Eventos</text>
        </g>
      </svg>
    </div>
  );
}

export default function Landing() {
  const [demo, setDemo] = useState({ name: "", email: "", company: "", message: "", website: "" });
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<{ kind: "success" | "error"; text: string } | null>(null);

  const updateDemo = (field: keyof typeof demo) => (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setDemo((current) => ({ ...current, [field]: event.target.value }));
  };

  const submitDemo = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (submitting) return;
    setSubmitting(true);
    setFeedback(null);
    try {
      const result = await api<{ accepted: boolean; notification_status?: "sent" | "not_configured" | "failed" }>(
        "/demo-requests/",
        "POST",
        demo,
      );
      const text = result.notification_status === "sent"
        ? "Recibimos tu solicitud y enviamos una notificación al equipo de AURA."
        : result.notification_status === "failed"
          ? "Tu solicitud quedó registrada, pero no pudimos enviar la notificación por correo."
          : "Tu solicitud quedó registrada. El correo de notificación aún está pendiente de configuración.";
      setFeedback({ kind: "success", text });
      setDemo({ name: "", email: "", company: "", message: "", website: "" });
    } catch (error) {
      setFeedback({ kind: "error", text: error instanceof Error ? error.message : "No se pudo enviar la solicitud." });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="landing">
      <header className="site-header">
        <a className="brand" href="#inicio" aria-label="AURA Intelligence, inicio">
          <BrandMark />
          <span className="brand-word">AURA Intelligence</span>
        </a>
        <nav className="site-nav" aria-label="Navegación principal">
          <a href="#capacidades">Soluciones</a>
          <a href="#plataforma">Plataforma</a>
          <a href="#sectores">Sectores</a>
          <a href="#seguridad">Seguridad</a>
          <a href="#solicitud">Contacto</a>
        </nav>
        <a className="header-cta" href="#solicitud">Solicitar una demostración</a>
      </header>

      <main>
        <section className="hero section-wrap" id="inicio">
          <div className="hero-copy">
            <div className="eyebrow">AURA INTELLIGENCE</div>
            <h1>Convierte los datos de<br className="desktop-break" /> tu empresa en<br className="desktop-break" /> <span className="gradient-text">decisiones<br className="desktop-break" /> inteligentes.</span></h1>
            <p className="hero-lede">Conecta información, descubre oportunidades y comprende mejor las operaciones de tu negocio con una plataforma de inteligencia empresarial pensada para decidir con fundamento.</p>
            <div className="hero-actions">
              <a className="button button-primary" href="#solicitud">Solicitar una demostración <span aria-hidden="true">↗</span></a>
              <a className="button button-secondary" href="#plataforma">Explorar la plataforma</a>
            </div>
          </div>
          <NetworkIllustration />
        </section>

        <section className="intro section-wrap" id="vision">
          <div className="section-kicker">01 / EL ENFOQUE</div>
          <div className="intro-copy">
            <h2>De datos dispersos a<br /><span className="muted-heading">una visión compartida.</span></h2>
            <p>AURA organiza la información esencial de tu empresa en un espacio donde las entidades y sus relaciones pueden entenderse en conjunto.</p>
          </div>
          <div className="intro-stamp"><span className="stamp-orbit">◎</span><span>CONOCER<br />CONECTAR<br />DECIDIR</span></div>
        </section>

        <section className="capabilities section-wrap" id="capacidades">
          <div className="section-heading">
            <div><div className="section-kicker">02 / CAPACIDADES</div><h2>El contexto cambia<br />lo que puedes ver.</h2></div>
            <p>Una base para entender la operación desde sus piezas y, sobre todo, desde las conexiones entre ellas.</p>
          </div>
          <div className="capability-grid">
            {capabilities.map((item) => (
              <article className="capability-card" key={item.number}>
                <div className="capability-top"><span>{item.number} / 03</span><span className="capability-icon" aria-hidden="true">{item.icon}</span></div>
                <h3>{item.title}</h3>
                <p>{item.text}</p>
                <span className="card-arrow" aria-hidden="true">↗</span>
              </article>
            ))}
          </div>
        </section>

        <section className="sectors section-wrap" id="sectores">
          <div className="section-kicker">03 / SECTORES</div>
          <div className="sectors-row">
            <h2>Inteligencia para<br /><span className="muted-heading">operaciones complejas.</span></h2>
            <div className="sector-tags"><span>Comercio</span><span>Distribución</span><span>Manufactura</span><span>Servicios</span></div>
          </div>
        </section>

        <section className="platform section-wrap" id="plataforma">
          <div className="platform-panel">
            <div className="platform-copy">
              <div className="section-kicker">03 / LA PLATAFORMA</div>
              <h2>Una lectura más completa del negocio.</h2>
              <p>Visualiza entidades, explora relaciones y consulta información de tu empresa desde una experiencia diseñada para dar contexto.</p>
              <a className="inline-link" href="#solicitud">Conversemos sobre una demostración <span aria-hidden="true">↗</span></a>
            </div>
            <div className="platform-visual" aria-hidden="true">
              <div className="platform-grid" />
              <div className="platform-orbit orbit-a" /><div className="platform-orbit orbit-b" />
              <div className="platform-core"><BrandMark /><span>AURA<br /><small>INTELLIGENCE</small></span></div>
              <span className="platform-node node-a">CLIENTES</span><span className="platform-node node-b">PRODUCTOS</span>
              <span className="platform-node node-c">OPERACIONES</span><span className="platform-node node-d">EVENTOS</span>
              <span className="platform-line line-a" /><span className="platform-line line-b" /><span className="platform-line line-c" /><span className="platform-line line-d" />
            </div>
          </div>
        </section>

        <section className="security section-wrap" id="seguridad">
          <span className="security-mark" aria-hidden="true">◇</span>
          <div><div className="section-kicker">04 / SEGURIDAD</div><h2>Acceso con contexto empresarial.</h2></div>
          <p>La autenticación y la separación por empresa forman parte de la base de AURA.</p>
        </section>

        <section className="closing section-wrap" id="solicitud">
          <div className="closing-rule" />
          <div className="section-kicker">SOLICITA UNA DEMOSTRACIÓN</div>
          <h2>Conoce AURA<br /><span className="gradient-text">en acción.</span></h2>
          <p className="demo-intro">Cuéntanos un poco sobre ti y tu empresa. Te mostraremos cómo AURA puede dar contexto a tus operaciones.</p>
          <form className="demo-form" onSubmit={submitDemo}>
            <label>Nombre<input name="name" value={demo.name} onChange={updateDemo("name")} autoComplete="name" placeholder="Tu nombre" maxLength={150} required /></label>
            <label>Correo de trabajo<input name="email" type="email" value={demo.email} onChange={updateDemo("email")} autoComplete="email" placeholder="nombre@empresa.com" maxLength={254} required /></label>
            <label>Empresa<input name="company" value={demo.company} onChange={updateDemo("company")} autoComplete="organization" placeholder="Nombre de tu empresa" maxLength={150} required /></label>
            <label>¿Qué te gustaría explorar?<textarea name="message" value={demo.message} onChange={updateDemo("message")} rows={3} placeholder="Cuéntanos brevemente qué necesitas" maxLength={2000} /></label>
            <div className="honeypot" aria-hidden="true"><label>Sitio web<input name="website" value={demo.website} onChange={updateDemo("website")} tabIndex={-1} autoComplete="off" /></label></div>
            <button className="button button-primary" type="submit" disabled={submitting}>{submitting ? "Enviando…" : "Enviar solicitud"} <span aria-hidden="true">↗</span></button>
            <p className="form-note">Tus datos se usarán para responder a esta solicitud de demostración.</p>
            {feedback && <p className={`form-feedback ${feedback.kind}`} role={feedback.kind === "error" ? "alert" : "status"}>{feedback.text}</p>}
          </form>
        </section>
      </main>

      <footer className="site-footer section-wrap">
        <a className="brand footer-brand" href="#inicio"><BrandMark /><span className="brand-word">AURA<small>INTELLIGENCE</small></span></a>
        <span>Inteligencia de datos empresariales.</span>
        <a href="#inicio">Volver arriba ↑</a>
      </footer>
    </div>
  );
}
