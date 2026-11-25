# Despliegue en producción (Render)

El repositorio incluye `render.yaml`, que crea en Render dos recursos:

- **Servicio web `aura-intelligence`**: FastAPI sirve la API y el sitio React. Render compila el sitio en cada despliegue y lo deja en `backend/static`.
- **Base PostgreSQL `aura-db`**: plan con copias de seguridad.

Costo aproximado: unos USD 13 al mes en total (servicio *Starter* más PostgreSQL *Basic 256 MB*). Confirma los precios en render.com/pricing antes de crear los recursos. Los planes gratuitos no sirven para clientes: el servicio se duerme y la base gratuita caduca.

## Antes de empezar

1. **Fusiona en `master`** el PR con estos cambios. Render despliega desde una rama de GitHub.
2. **No hace falta recompilar el frontend a mano.** Render ejecuta `npm ci` y `npm run build` en `frontend/` en cada despliegue (ver la sección 6).

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

Abre el servicio en Render, ve a **Shell** y entra primero en `backend`. Desde que el servicio no usa `rootDir`, la Shell abre en la raíz del repositorio (la línea termina en `~/project/src$`):

```bash
cd backend
```

Luego crea el usuario:

```bash
python scripts/create_client.py --company "EDITH Intelligence" --name "Tu nombre" --email tu-correo@dominio.com
```

Usa para tu usuario el mismo correo que pusiste en `ADMIN_EMAILS`, así ves el menú **Solicitudes**. El script imprime una contraseña temporal una sola vez; al entrar, cámbiala en **Cuenta**. Para cada cliente nuevo, repite el comando con sus datos y envíale la contraseña por un canal distinto al del correo de bienvenida (por ejemplo, WhatsApp).

Para tus demos de venta puedes crear la empresa ficticia con `python scripts/seed_demo.py --email demo@tudominio.com`. Ten en cuenta que comparte la base con tus clientes. Si prefieres separarla, crea un segundo servicio solo para demostraciones.

## 3. Dominio propio y HTTPS

1. Compra el dominio, por ejemplo en Namecheap, GoDaddy o un registrador .co.
2. En Render ve a **Settings → Custom Domains → Add**, escribe `www.tudominio.com` y luego `tudominio.com`.
3. En tu registrador crea los registros DNS que Render te indique: un `CNAME` para `www` y un `A` o `ALIAS` para el dominio raíz.
4. Render emite el certificado HTTPS automáticamente cuando el DNS propaga, normalmente en menos de una hora.
5. Cambia `contactEmail` en `frontend/src/siteConfig.ts` por el correo de tu dominio y fusiona. Render recompila el sitio solo.

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

Estos comandos se ejecutan dentro de `backend` (`cd backend` al abrir la Shell). Si al pegar sale `\E[200~`, escribe primero a mano `bind 'set enable-bracketed-paste off'`.

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

## 6. Compilación del sitio en Render

### Qué cambió (2026-11-25)

Antes, `render.yaml` usaba `rootDir: backend` y solo hacía `pip install`. Render servía el `backend/static` guardado en git. Si alguien cambiaba `frontend/src` y olvidaba ejecutar `npm run build` y confirmar `backend/static`, producción quedaba con el sitio viejo y nadie se enteraba.

Ahora el servicio no tiene `rootDir`, así que los comandos parten de la raíz del repositorio:

| Campo | Valor |
|---|---|
| Root Directory | vacío |
| Build Command | `node --version && npm --version && cd frontend && npm ci --include=dev && npm run build && cd .. && pip install -r backend/requirements.txt` |
| Start Command | `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT --proxy-headers --forwarded-allow-ips="*"` |
| `NODE_VERSION` | `22.22.0` |

- `npm run build` ejecuta `tsc --noEmit` y `vite build`. Vite escribe en `backend/static` (`frontend/vite.config.ts`) y `backend/main.py` sirve el sitio desde esa carpeta. Desde el 2026-11-25 la carpeta no se guarda en git (ver más abajo).
- `--include=dev` hace falta porque TypeScript y Vite son dependencias de desarrollo.
- Sin `rootDir`, cualquier fusión en `master` dispara un despliegue, también si solo cambia `frontend/`. Con `rootDir: backend`, Render ignora los cambios de fuera de `backend/`.
- Si `tsc` encuentra un error de tipos, el build falla y Render mantiene la versión anterior funcionando. Es preferible a publicar un sitio roto.

### Riesgo del primer despliegue

La documentación de Render no dice de forma explícita que el runtime Python traiga Node. Por eso el build empieza con `node --version && npm --version`:

- Si el log de build muestra las dos versiones y luego `vite build` con `✓ built`, todo está bien.
- Si falla con `node: command not found`, el despliegue se cancela y producción sigue con la versión anterior. En ese caso, vuelve a poner temporalmente `rootDir: backend` y el `buildCommand` antiguo, y avisa para cambiar a un servicio Docker (el `Dockerfile` ya compila el sitio).
- `NODE_VERSION` está documentada para servicios Node. Si Render la ignora en Python, usará su Node por defecto (24.x en servicios nuevos), que también compila este sitio. El log muestra cuál usó.

### Qué debes hacer en Render

1. Fusiona el PR en `master`.
2. Si el servicio se creó con el Blueprint y está sincronizado, Render aplica `render.yaml` solo. Compruébalo en **Settings → Build & Deploy**: Root Directory vacío y los comandos de la tabla.
3. Si el servicio no está sincronizado con el Blueprint, cambia esos tres campos a mano en **Settings → Build & Deploy** y añade `NODE_VERSION=22.22.0` en **Environment**. Después pulsa **Manual Deploy → Deploy latest commit**.
4. Revisa el log de build: versiones de Node y npm, `vite build` y `✓ built`.
5. Abre `/health`, `/`, `/login` y `/app/customers` en el dominio. Las cuatro deben cargar.
6. Recuerda que en la **Shell** ahora hay que hacer `cd backend` antes de los scripts.

### `backend/static` ya no se guarda en git

Se quitó del repositorio el 2026-11-25, después de comprobar un despliegue correcto con el build nuevo. La carpeta está en `.gitignore`.

- Render y el `Dockerfile` la generan en cada despliegue. Si el build del frontend falla, no se publica nada y sigue la versión anterior.
- `backend/main.py` arranca aunque la carpeta no exista. La API funciona igual, `/` responde con el mensaje de la API y `/login`, `/privacidad` y `/app/...` devuelven 404 con el aviso `Sitio no compilado`.
- En local, para ver el sitio desde `uvicorn` en el puerto 8000, compila antes con `cd frontend; npm run build`. Para el desarrollo diario sigue usando `dev.ps1`, que abre Vite en el puerto 5173.
- Para volver atrás, basta revertir el commit que quitó la carpeta: vuelve a quedar en git y `.gitignore` deja de ignorarla.

## Lista de verificación antes del primer cliente

- [ ] El log del último despliegue muestra `vite build` y `✓ built`.
- [ ] `/health` responde en el dominio propio con HTTPS.
- [ ] Puedes iniciar sesión con tu usuario y ves el menú **Solicitudes**.
- [ ] Enviaste una solicitud de demostración de prueba y llegó al correo, o al menos aparece en **Solicitudes**.
- [ ] Probaste importar un CSV y la búsqueda en Clientes y Productos.
- [ ] Probaste restaurar una copia de seguridad.
- [ ] `/login` no muestra "Crear empresa nueva".
