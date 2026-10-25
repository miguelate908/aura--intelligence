import { Link } from "react-router-dom";
import { SITE } from "../siteConfig";
import "../landing-extra.css";

export default function Privacy() {
  const mail = SITE.contactEmail ? <a href={`mailto:${SITE.contactEmail}`}>{SITE.contactEmail}</a> : <em>[correo pendiente]</em>;
  return (
    <div className="x-legal">
      <Link to="/">← Volver al inicio</Link>
      <h1>Política de privacidad</h1>
      <p><b>Borrador informativo.</b> Debe ser revisado por un profesional legal antes de usarse con datos reales.</p>
      <h2>Responsable</h2>
      <p>{SITE.legalName || <em>[responsable pendiente]</em>}. Contacto: {mail}.</p>
      <h2>Datos que recogemos</h2>
      <p>Del formulario de demostración: nombre, correo, empresa, cargo, sector, tamaño de la organización (opcional), necesidad, mensaje (opcional), fecha de envío y tu consentimiento. Para cuentas de la plataforma: nombre de la empresa, tu nombre, correo y contraseña (solo como hash).</p>
      <p>Para limitar abusos, el servidor usa temporalmente tu dirección IP en memoria; no se guarda en la base de datos.</p>
      <h2>Para qué los usamos</h2>
      <p>Responder tu solicitud de demostración y prestar el servicio a quienes tienen una cuenta.</p>
      <h2>Con quién los compartimos</h2>
      <p>Cuando el servicio de correo está configurado, el contenido de tu solicitud se envía como notificación al correo del equipo a través del proveedor SMTP que haya configurado el responsable. <em>[Proveedor de correo pendiente de nombrar.]</em> No usamos otros terceros para estos datos.</p>
      <h2>Conservación</h2>
      <p>Las solicitudes de demostración se eliminan automáticamente a los 7 días. Las copias de seguridad de la base de datos, si el responsable las realiza, pueden conservarlas más tiempo. <em>[Plazo de los datos de cuentas pendiente de definir.]</em></p>
      <h2>Tus derechos</h2>
      <p>Puedes solicitar acceso, corrección o eliminación de tus datos y retirar tu consentimiento escribiendo a {mail}. La normativa aplicable depende de tu país: confírmala con un asesor legal.</p>
    </div>
  );
}
