import { Link } from "react-router-dom";
import { SITE } from "./siteConfig";
import "./landing.css";

export default function Privacy() {
  const mail = SITE.contactEmail ? <a href={`mailto:${SITE.contactEmail}`}>{SITE.contactEmail}</a> : <em>[correo de contacto pendiente de configurar]</em>;
  const who = SITE.legalName || <em>[responsable pendiente de configurar]</em>;
  return (
    <div className="aura-landing">
      <header><div className="w"><Link className="logo" to="/"><i />AURA Intelligence</Link><a className="btn p" href="/#contacto">Solicitar una demostración</a></div></header>
      <main><section><div className="w legal">
        <h1>Política de privacidad</h1>
        <p className="sub"><b>Borrador informativo.</b> Debe ser revisado por un profesional legal y completado con los datos del responsable antes de publicarse.</p>
        <h2>Responsable</h2><p>{who}. Contacto: {mail}.</p>
        <h2>Datos que recogemos</h2>
        <p><b>Formulario de contacto:</b> nombre, correo, empresa, cargo, sector, tamaño de la organización (opcional), necesidad, mensaje (opcional), fecha de envío y el consentimiento que otorgas.</p>
        <p><b>Cuenta en la plataforma:</b> nombre de la empresa, tu nombre, correo y contraseña (almacenada solo como hash). Los registros que cargues en el panel pertenecen a tu empresa.</p>
        <p>Para limitar abusos, el servidor usa temporalmente tu dirección IP en memoria. No la guardamos en la base de datos.</p>
        <h2>Para qué los usamos</h2>
        <p>Responder tu solicitud de demostración o contacto comercial, y prestar el servicio a quienes tienen una cuenta. No usamos los datos del formulario para fines distintos sin tu consentimiento.</p>
        <h2>Con quién los compartimos</h2>
        <p>Hoy no hay integraciones con terceros configuradas para los datos del formulario ni envío automático de correos. Si eso cambia, esta política se actualizará antes.</p>
        <h2>Conservación</h2><p>Las solicitudes del formulario de contacto se conservan durante 1 semana (7 días) y después se eliminan automáticamente de la base de datos. <em>[Plazo para los datos de cuentas pendiente de definir por el responsable.]</em></p>
        <h2>Tus derechos</h2><p>Puedes solicitar acceso, corrección o eliminación de tus datos, y retirar tu consentimiento, escribiendo a {mail}. La normativa aplicable depende de tu país: confírmala con un asesor legal.</p>
        <p><Link to="/">← Volver al inicio</Link></p>
      </div></section></main>
    </div>
  );
}
