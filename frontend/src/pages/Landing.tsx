import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { SITE } from "../siteConfig";
import EdithMark from "../assets/edith-mark.svg";
import EdithLogo from "../assets/edith-logo.svg";
import EdithLogoLight from "../assets/edith-logo-light.svg";
import { ThemeToggle } from "../theme";
import "../landing-extra.css";

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

const problems: [string, string][] = [
  ["Información dispersa", "Valor: un punto único donde los datos se relacionan."],
  ["Sin visión unificada", "Valor: panorama conectado de clientes, productos y bodegas."],
  ["Seguimiento manual", "Valor: registro estructurado de eventos y operaciones."],
  ["Riesgos y oportunidades ocultos", "Valor: exploración de relaciones para detectarlos."],
  ["Decisiones sin contexto", "Valor: datos relacionados para decidir con más criterio."],
  ["Poca visibilidad de inventario", "Valor: productos y bodegas organizados por empresa."],
];
const features: [string, string, "ok" | "dev"][] = [
  ["Clientes y operaciones", "Registro y organización de clientes de tu empresa.", "ok"],
  ["Productos y bodegas", "Inventario por empresa: productos y almacenes.", "ok"],
  ["Relaciones y eventos", "Eventos automáticos y exploración de relaciones en grafo.", "ok"],
  ["Asistente de consultas", "Responde preguntas sobre clientes, productos, bodegas y actividad con reglas predefinidas. No es IA generativa.", "ok"],
  ["Inteligencia artificial", "Explicaciones y recomendaciones en lenguaje natural.", "dev"],
  ["Oportunidades y riesgos", "Identificación de patrones que merecen atención.", "dev"],
];
const sectorCases: [string, string][] = [
  ["Logística y distribución", "Relacionar bodegas, productos y eventos de movimiento."],
  ["Comercio y retail", "Conectar clientes con los productos que compran."],
  ["Manufactura", "Seguir referencias de producto por bodega."],
  ["Empresas de tecnología", "Unificar cuentas de clientes y eventos de su relación."],
];
const steps = ["Registrar información empresarial.", "Organizar y relacionar los datos.", "Consultar y explorar patrones.", "Obtener análisis útiles.", "Evaluar y decidir las acciones."];
const securityItems: [string, string][] = [
  ["Acceso con sesión", "El panel requiere iniciar sesión. Las sesiones caducan a los 30 minutos."],
  ["Contraseñas protegidas", "Se almacenan con hash bcrypt y se exigen 12 caracteres como mínimo."],
  ["Datos por empresa", "Cada registro pertenece a una empresa y el servidor filtra las consultas por la empresa del usuario autenticado."],
  ["Límite de envíos", "El formulario de contacto limita los envíos repetidos desde una misma IP."],
  ["Consentimiento", "Guardamos tu solicitud solo si aceptas el tratamiento de tus datos."],
];
// Precios de referencia; mantenerlos iguales a docs/comercial/PLAN-COMERCIAL.md.
const plans: { name: string; price: string; unit: string; items: string[]; featured?: boolean }[] = [
  { name: "Piloto 30 días", price: "COP 1.200.000", unit: "pago único", featured: true, items: [
    "Cargamos tus archivos de Excel o CSV (hasta 5.000 registros)",
    "Configuración de la cuenta de tu empresa",
    "Dos sesiones de trabajo con nuestro equipo",
    "Informe de hallazgos sobre tus datos",
    "Se descuenta del plan anual si continúas",
  ] },
  { name: "Esencial", price: "COP 290.000", unit: "/ mes", items: [
    "Hasta 10.000 registros",
    "Una recarga de datos asistida al mes",
    "Soporte por correo en 2 días hábiles",
  ] },
  { name: "Profesional", price: "COP 690.000", unit: "/ mes", items: [
    "Hasta 50.000 registros",
    "Recargas de datos asistidas sin límite",
    "Reunión mensual de revisión con informe",
    "Soporte prioritario en 1 día hábil",
  ] },
];
const EMPTY = { name: "", email: "", company: "", job_title: "", sector: "", company_size: "", need: "", message: "", website: "" };

function BrandMark() {
  return <img className="brand-mark" src={EdithMark} alt="" aria-hidden="true" />;
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
        <ellipse className="graph-aura" cx="310" cy="215" rx="275" ry="205" fill="url(#graphAura)" />
        <g stroke="url(#graphLink)" strokeWidth="1.6">
          <path d="M310 218 124 100M310 218 495 106M310 218 104 323M310 218 510 335" />
          <path d="M124 100 495 106M104 323 510 335" strokeDasharray="5 7" opacity=".72" />
        </g>
        <circle cx="124" cy="100" r="27" fill="#20b9d5" fillOpacity=".63" />
        <circle cx="495" cy="106" r="27" fill="#3475e8" fillOpacity=".67" />
        <circle cx="310" cy="218" r="31" fill="#8854e9" fillOpacity=".62" />
        <circle cx="104" cy="323" r="25" fill="#3475e8" fillOpacity=".58" />
        <circle cx="510" cy="335" r="26" fill="#20b9d5" fillOpacity=".61" />
        <g fill="currentColor" fontFamily="Inter, system-ui, sans-serif" fontSize="13" textAnchor="middle">
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
  const [demo, setDemo] = useState(EMPTY);
  const [consent, setConsent] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState<{ kind: "success" | "error"; text: string } | null>(null);

  const updateDemo = (field: keyof typeof demo) => (event: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
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
        { ...demo, company_size: demo.company_size || null, consent },
      );
      const text = result.notification_status === "sent"
        ? "Recibimos tu solicitud y enviamos una notificación al equipo de EDITH."
        : result.notification_status === "failed"
          ? "Tu solicitud quedó registrada, pero no pudimos enviar la notificación por correo."
          : "Tu solicitud quedó registrada. El correo de notificación aún está pendiente de configuración.";
      setFeedback({ kind: "success", text });
      setDemo(EMPTY);
      setConsent(false);
    } catch (error) {
      setFeedback({ kind: "error", text: error instanceof Error ? error.message : "No se pudo enviar la solicitud." });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="landing">
      <header className="site-header">
        <a className="brand" href="#inicio" aria-label="EDITH Intelligence, inicio">
          <img className="brand-logo on-dark" src={EdithLogo} alt="" aria-hidden="true" />
          <img className="brand-logo on-light" src={EdithLogoLight} alt="" aria-hidden="true" />
        </a>
        <nav className="site-nav" aria-label="Navegación principal">
          <a href="#capacidades">Soluciones</a>
          <a href="#plataforma">Plataforma</a>
          <a href="#sectores">Sectores</a>
          <a href="#planes">Planes</a>
          <a href="#seguridad">Seguridad</a>
          <a href="#solicitud">Contacto</a>
          <Link to="/login">Acceder</Link>
        </nav>
        <ThemeToggle />
        <a className="header-cta" href="#solicitud">Solicitar una demostración</a>
      </header>

      <main>
        <section className="hero section-wrap" id="inicio">
          <div className="hero-copy">
            <div className="eyebrow">EDITH INTELLIGENCE</div>
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
            <p>EDITH organiza la información esencial de tu empresa en un espacio donde las entidades y sus relaciones pueden entenderse en conjunto.</p>
          </div>
          <div className="intro-stamp"><span className="stamp-orbit">◎</span><span>CONOCER<br />CONECTAR<br />DECIDIR</span></div>
        </section>

        <section className="section-wrap x-section" id="problemas">
          <div className="section-kicker">PROBLEMAS QUE RESOLVEMOS</div>
          <h2>Cuando la información vive en lugares distintos, decidir cuesta más.</h2>
          <div className="x-grid">
            {problems.map(([t, p]) => (<article className="x-card" key={t}><h3>{t}</h3><p>{p}</p></article>))}
          </div>
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
            <div className="x-grid x-grid-2">{sectorCases.map(([t, p]) => (<article className="x-card" key={t}><h3>{t}</h3><p>{p}</p></article>))}</div>
          </div>
        </section>

        <section className="platform section-wrap" id="plataforma">
          <div className="platform-panel">
            <div className="platform-copy">
              <div className="section-kicker">04 / LA PLATAFORMA</div>
              <h2>Una lectura más completa del negocio.</h2>
              <p>Visualiza entidades, explora relaciones y consulta información de tu empresa desde una experiencia diseñada para dar contexto.</p>
              <a className="inline-link" href="#solicitud">Conversemos sobre una demostración <span aria-hidden="true">↗</span></a>
            </div>
            <div className="platform-visual" aria-hidden="true">
              <div className="platform-grid" />
              <div className="platform-orbit orbit-a" /><div className="platform-orbit orbit-b" />
              <div className="platform-core"><BrandMark /><span>EDITH<br /><small>INTELLIGENCE</small></span></div>
              <span className="platform-node node-a">CLIENTES</span><span className="platform-node node-b">PRODUCTOS</span>
              <span className="platform-node node-c">OPERACIONES</span><span className="platform-node node-d">EVENTOS</span>
              <span className="platform-line line-a" /><span className="platform-line line-b" /><span className="platform-line line-c" /><span className="platform-line line-d" />
            </div>
          </div>
        </section>

        <section className="section-wrap x-section" id="estado">
          <div className="section-kicker">ESTADO DEL PRODUCTO</div>
          <h2>Qué está operativo hoy y qué está en desarrollo.</h2>
          <div className="x-grid">
            {features.map(([t, p, st]) => (
              <article className="x-card" key={t}>
                <span className={`x-badge ${st}`}>{st === "ok" ? "Operativo" : "En desarrollo"}</span>
                <h3>{t}</h3><p>{p}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="section-wrap x-section" id="como-funciona">
          <div className="section-kicker">CÓMO FUNCIONA</div>
          <h2>Del registro a la decisión.</h2>
          <ol className="x-steps">{steps.map((t) => <li key={t}>{t}</li>)}</ol>
        </section>

        <section className="section-wrap x-section" id="planes">
          <div className="section-kicker">PLANES</div>
          <h2>Empieza con un piloto de 30 días. Continúa si te sirve.</h2>
          <div className="x-plans">
            {plans.map((p) => (
              <article className={`x-card x-plan${p.featured ? " featured" : ""}`} key={p.name}>
                {p.featured && <span className="x-badge ok">Recomendado para empezar</span>}
                <h3>{p.name}</h3>
                <div className="x-price">{p.price} <small>{p.unit}</small></div>
                <ul>{p.items.map((i) => <li key={i}>{i}</li>)}</ul>
                <a className="button button-secondary" href="#solicitud">{p.featured ? "Solicitar el piloto" : "Hablar con ventas"}</a>
              </article>
            ))}
          </div>
          <p className="x-note">Precio por empresa. Pago anual: dos meses sin costo. Valores antes de impuestos. Desarrollos a medida bajo cotización.</p>
        </section>

        <section className="section-wrap x-section" id="seguridad">
          <div className="section-kicker">05 / SEGURIDAD Y PRIVACIDAD</div>
          <h2>Solo describimos lo que el producto hace hoy.</h2>
          <div className="x-grid">
            {securityItems.map(([t, p]) => (<article className="x-card" key={t}><h3>{t}</h3><p>{p}</p></article>))}
          </div>
          <p className="x-note">No declaramos certificaciones ni cumplimiento normativo. <Link to="/privacidad">Ver política de privacidad</Link>.</p>
        </section>

        <section className="closing section-wrap" id="solicitud">
          <div className="closing-rule" />
          <div className="section-kicker">SOLICITA UNA DEMOSTRACIÓN</div>
          <h2>Conoce EDITH<br /><span className="gradient-text">en acción.</span></h2>
          <p className="demo-intro">Cuéntanos un poco sobre ti y tu empresa. Te mostraremos cómo EDITH puede dar contexto a tus operaciones.</p>
          <form className="demo-form" onSubmit={submitDemo}>
            <label>Nombre<input name="name" value={demo.name} onChange={updateDemo("name")} autoComplete="name" placeholder="Tu nombre" maxLength={150} required /></label>
            <label>Correo de trabajo<input name="email" type="email" value={demo.email} onChange={updateDemo("email")} autoComplete="email" placeholder="nombre@empresa.com" maxLength={254} required /></label>
            <label>Empresa<input name="company" value={demo.company} onChange={updateDemo("company")} autoComplete="organization" placeholder="Nombre de tu empresa" maxLength={150} required /></label>
            <label>Cargo o función<input name="job_title" value={demo.job_title} onChange={updateDemo("job_title")} autoComplete="organization-title" maxLength={150} required /></label>
            <label>Sector
              <select name="sector" value={demo.sector} onChange={updateDemo("sector")} required>
                <option value="">Selecciona…</option>
                <option value="logistica">Logística y distribución</option>
                <option value="retail">Comercio y retail</option>
                <option value="manufactura">Manufactura</option>
                <option value="tecnologia">Tecnología</option>
                <option value="servicios">Servicios profesionales</option>
                <option value="datos">Grandes volúmenes de información</option>
                <option value="otro">Otro</option>
              </select>
            </label>
            <label>Tamaño de la organización (opcional)
              <select name="company_size" value={demo.company_size} onChange={updateDemo("company_size")}>
                <option value="">—</option><option>1-10</option><option>11-50</option><option>51-200</option><option>201-1000</option><option>Más de 1000</option>
              </select>
            </label>
            <label>Principal necesidad o problema<textarea name="need" value={demo.need} onChange={updateDemo("need")} rows={3} minLength={10} maxLength={2000} required /></label>
            <label>Mensaje adicional (opcional)<textarea name="message" value={demo.message} onChange={updateDemo("message")} rows={2} maxLength={2000} /></label>
            <div className="honeypot" aria-hidden="true"><label>Sitio web<input name="website" value={demo.website} onChange={updateDemo("website")} tabIndex={-1} autoComplete="off" /></label></div>
            <label className="x-consent"><input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} required /> Acepto el tratamiento de mis datos personales según la <Link to="/privacidad" target="_blank">política de privacidad</Link>.</label>
            <button className="button button-primary" type="submit" disabled={submitting}>{submitting ? "Enviando…" : "Enviar solicitud"} <span aria-hidden="true">↗</span></button>
            <p className="form-note">Tus datos se usarán para responder a esta solicitud de demostración.</p>
            {feedback && <p className={`form-feedback ${feedback.kind}`} role={feedback.kind === "error" ? "alert" : "status"}>{feedback.text}</p>}
          </form>
        </section>
      </main>

      <footer className="site-footer section-wrap">
        <a className="brand footer-brand" href="#inicio" aria-label="EDITH Intelligence, inicio"><img className="brand-logo on-dark" src={EdithLogo} alt="" aria-hidden="true" /><img className="brand-logo on-light" src={EdithLogoLight} alt="" aria-hidden="true" /></a>
        <span>Inteligencia de datos empresariales.</span>
        <span className="x-foot">
          {SITE.contactEmail && <><a href={`mailto:${SITE.contactEmail}`}>{SITE.contactEmail}</a> · </>}
          <Link to="/privacidad">Privacidad</Link>
        </span>
        <a href="#inicio">Volver arriba ↑</a>
      </footer>
    </div>
  );
}
