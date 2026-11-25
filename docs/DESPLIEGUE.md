# Despliegue en producción (Render)

El repositorio incluye `render.yaml`, que crea en Render dos recursos:

- **Servicio web `aura-intelligence`**: FastAPI sirve la API y el sitio ya compilado en `backend/static`.
- **Base PostgreSQL `aura-db`**: plan con copias de seguridad.

Costo aproximado: unos USD 13 al mes en total (servicio *Starter* más PostgreSQL *Basic 256 MB*). Confirma los precios en render.com/pricing antes de crear los recursos. Los planes gratuitos no sirven para clientes: el servicio se duerme y la base gratuita caduca.

## Antes de empezar

1. **Fusiona en `master`** el PR con estos cambios. Render despliega desde una rama de GitHub.
2. **Recompila el frontend si cambiaste algo en `frontend/`** y confirma `backend/static`. Render no compila el frontend.
   ```powershell
   cd frontend; npm run build
   ```

## 1. Crear los recursos (una sola vez)

1. Crea una cuenta en https://render.com con tu usuario de GitHub. Da acceso solo al repositorio `aura--intelligence`.
2. Ve a **New → Blueprint**, elige el repositorio y la rama `master`. Render lee `render.yaml`.
3. Render pide los valores marcados como secretos:

   | Variable | Qué poner |
   |---|---|
   | `ADMIN_EMAILS` | Tu correo de acceso al panel. Es el que ve el menú **Solicitudes**. |
   | `DEMO_REQUEST_EMAIL` | El correo donde quieres recibir las solicitudes de demostración. |
   | `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | Los datos de tu proveedor de correo. Ver la sección 4. Puedes dejarlos vacíos al principio: las solicitudes se guardan igual y las ves en el panel. |

   `JWT_SECRET_KEY` se genera sola y `DATABASE_URL` se conecta sola a la base. No las escribas.
4. Pulsa **Apply**. El primer despliegue tarda unos minutos.
5. Abre la URL `https://aura-intelligence-xxxx.onrender.com/health`. Debe responder `{"status":"ok"}`.

## 2. Crear tu usuario y los de tus clientes

El registro público está desactivado en producción (`REGISTRATION_ENABLED=false`). Así nadie crea cuentas gratis y cada cuenta corresponde a un cliente que firmó un piloto.

Abre el servicio en Render, ve a **Shell** y ejecuta el comando. La Shell ya abre dentro de la carpeta `backend` (la línea termina en `~/project/src/backend$`), así que no hace falta `cd backend`:

```bash
python scripts/create_client.py --company "AURA Intelligence" --name "Tu nombre" --email tu-correo@dominio.com
```

Usa para tu usuario el mismo correo que pusiste en `ADMIN_EMAILS`, así ves el menú **Solicitudes**. El script imprime una contraseña temporal una sola vez; al entrar, cámbiala en **Cuenta**. Para cada cliente nuevo, repite el comando con sus datos y envíale la contraseña por un canal distinto al del correo de bienvenida (por ejemplo, WhatsApp).

Para tus demos de venta puedes crear la empresa ficticia con `python scripts/seed_demo.py --email demo@tudominio.com`. Ten en cuenta que comparte la base con tus clientes. Si prefieres separarla, crea un segundo servicio solo para demostraciones.

## 3. Dominio propio y HTTPS

1. Compra el dominio, por ejemplo en Namecheap, GoDaddy o un registrador .co.
2. En Render ve a **Settings → Custom Domains → Add**, escribe `www.tudominio.com` y luego `tudominio.com`.
3. En tu registrador crea los registros DNS que Render te indique: un `CNAME` para `www` y un `A` o `ALIAS` para el dominio raíz.
4. Render emite el certificado HTTPS automáticamente cuando el DNS propaga, normalmente en menos de una hora.
5. Cambia `contactEmail` en `frontend/src/siteConfig.ts` por el correo de tu dominio, recompila y fusiona.

## 4. Correo para las notificaciones

Cada solicitud de demostración envía un aviso a `DEMO_REQUEST_EMAIL`. Al pulsar **Responder** en ese aviso, la respuesta va directo al interesado.

### Opción recomendada: Brevo (gratis hasta 300 correos al día)

Es la configuración que está en producción. Gmail suele cortar los inicios de sesión que llegan desde servidores como Render, aunque la contraseña de aplicación esté bien. Brevo está hecho para enviar desde servidores.

1. Crea una cuenta en https://www.brevo.com (plan **Free**).
2. Verifica el remitente: tu nombre → **Senders, Domains & Dedicated IPs** → **Senders** → **Add sender**, con el correo que usarás en `SMTP_FROM`.
3. Tu nombre → **SMTP & API** → pestaña **SMTP**:
   - copia el **Login**; termina en `@smtp-brevo.com`;
   - pulsa **Generate a new SMTP key** y cópiala; empieza por `xsmtpsib-`. La API key (`xkeysib-`) no sirve aquí.
4. En **Environment** del servicio en Render:

   | Variable | Valor |
   |---|---|
   | `SMTP_HOST` | `smtp-relay.brevo.com` |
   | `SMTP_PORT` | `587` |
   | `SMTP_STARTTLS` | `true` |
   | `SMTP_USER` | el **Login** de Brevo (`...@smtp-brevo.com`), **no** tu correo |
   | `SMTP_PASSWORD` | la **SMTP key** |
   | `SMTP_FROM` | el remitente verificado en el paso 2 |
   | `DEMO_REQUEST_EMAIL` | el correo donde quieres recibir los avisos |

5. Pulsa **Save, rebuild, and deploy**. No uses **Save only**: el servicio no ve los valores nuevos hasta que se vuelve a desplegar.

Si el remitente es un Gmail, los primeros avisos pueden caer en **Spam**. Márcalos como "No es spam". Con un dominio propio verificado en Brevo esto desaparece.

### Alternativa: Google Workspace o Gmail

- `SMTP_HOST=smtp.gmail.com`, `SMTP_PORT=587`, `SMTP_STARTTLS=true`.
- `SMTP_USER` y `SMTP_FROM` con tu correo.
- `SMTP_PASSWORD` con una **contraseña de aplicación** de 16 letras sin espacios, no la contraseña normal. Exige tener activada la verificación en dos pasos.

### Probar el envío desde la Shell de Render

Si al pegar sale `\E[200~`, escribe primero a mano `bind 'set enable-bracketed-paste off'`.

Revisa que las variables tengan valor, sin mostrarlos:

```bash
python -c "import os;[print(k, 'OK' if os.getenv(k,'').strip() else 'VACIA') for k in ['SMTP_HOST','SMTP_USER','SMTP_PASSWORD','SMTP_FROM','DEMO_REQUEST_EMAIL']]"
```

Envía un aviso de prueba. Debe imprimir `sent`:

```bash
python -c "from types import SimpleNamespace as S; from routers.demo_requests import _send_notification as f; print(f(S(id=0,name='Prueba',email='prueba@example.com',company_name='Prueba SMTP',job_title='-',sector='-',company_size=None,need='Prueba de correo',message='')))"
```

| Resultado | Qué significa |
|---|---|
| `sent` | El correo salió. Si no lo ves, búscalo en Spam. |
| `not_configured` | `SMTP_HOST`, `SMTP_FROM` o `DEMO_REQUEST_EMAIL` está vacía en el servidor. Revisa los valores y usa **Save, rebuild, and deploy**. |
| `535 Authentication failed` | Usuario o clave incorrectos. En Brevo, `SMTP_USER` debe ser el Login `...@smtp-brevo.com`. |
| `Connection unexpectedly closed` | Gmail cortó el inicio de sesión desde Render. Cambia a Brevo. |

En el panel, cada solicitud muestra **Correo de aviso al equipo: enviado / no enviado**.

## 5. Operación diaria

- **Nuevas versiones:** cada fusión en `master` se despliega sola (`autoDeploy: true`). Si un despliegue falla, Render mantiene la versión anterior funcionando.
- **Copias de seguridad:** el plan de PostgreSQL las hace a diario. Antes del primer piloto, prueba una restauración en **aura-db → Recovery**.
- **Registros de errores:** en el servicio, ve a **Logs**.
- **Varias instancias:** los límites de intentos de login y del formulario viven en memoria. Si algún día escalas a más de una instancia, hay que moverlos a Redis (ver `backend/core/ratelimit.py`).

## Lista de verificación antes del primer cliente

- [ ] `/health` responde en el dominio propio con HTTPS.
- [ ] Puedes iniciar sesión con tu usuario y ves el menú **Solicitudes**.
- [ ] Enviaste una solicitud de demostración de prueba y llegó al correo, o al menos aparece en **Solicitudes**.
- [ ] Probaste importar un CSV y la búsqueda en Clientes y Productos.
- [ ] Probaste restaurar una copia de seguridad.
- [ ] `/login` no muestra "Crear empresa nueva".
