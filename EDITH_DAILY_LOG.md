# EDITH — Registro diario

## 2026-11-25 — Actualización de dependencias del frontend (avisos de `npm audit`)

**Rama:** `claude/magical-cerf-238ltt` (creada desde `master` en `559e1f5`; sin fusión, lista para revisión)

### Motivo

La supervisión de hoy encontró 4 avisos de `npm audit` en `frontend/` (1 alto, 3 moderados): `vite 5.4.21` + `esbuild <=0.24.2` (solo afectan al servidor de desarrollo) y `react-router-dom`/`react-router 6.30.6` (GHSA-wrjc-x8rr-h8h6, GHSA-337j-9hxr-rhxg). Corregirlos exigía subir de versión mayor.

### Cambios

| Paquete | Antes | Después |
|---|---|---|
| vite | ^5.4.10 (5.4.21) | ^6.4.6 (esbuild 0.25.12) |
| @vitejs/plugin-react | ^4.3.3 | ^5.2.0 |
| react-router-dom | ^6.28.0 (6.30.6) | ^7.18.7 (react-router 7.18.7) |

- Se eligió Vite 6.4.x (no 8.x) porque corrige los avisos con el menor salto y mantiene compatibilidad con Node 18/20/22.
- No hizo falta tocar `App.tsx`, `pages/*.tsx` ni `vite.config.ts`: las importaciones desde `react-router-dom` (`Navigate`, `NavLink`, `Outlet`, `Route`, `Routes`, `Link`, `BrowserRouter`) siguen funcionando en v7.
- `backend/static/` se regeneró con el nuevo build (Render sirve esos archivos ya compilados).

### Verificación

- `npm ci` y `npm run build` (tsc + vite) sin errores; `npm audit`: **0 vulnerabilidades**.
- `python -m pytest -q` en `backend/` (SQLite): **33 pasadas**. Nota: `pytest -q` a secas falla al importar `database`/`core` porque no añade `backend/` al `sys.path`; el CI ya usa `python -m pytest`.
- Navegador (Chromium) con `uvicorn main:app`: `/`, `/login` y `/privacidad` responden 200 y renderizan; `/app/customers` sin sesión redirige a `/login`; tras iniciar sesión carga «Clientes» y la navegación del panel funciona. Sin errores de JavaScript.
- Único error de consola: `GET /inventory` → 404 desde el Resumen. Es previo a este cambio (el backend aún no incluye `routers.inventory`, ver `backend/main.py`) y la página lo maneja sin romperse.

### Node del `Dockerfile`

`@vitejs/plugin-react` 5 exige Node `^20.19.0 || >=22.12.0`; Vite 6 admite `^20`. La imagen `node:20-alpine` trae hoy Node 20.20.2, y con esa versión `npm ci` y el build salieron idénticos (mismos hashes) sin avisos de engine, así que era compatible. Aun así, con aprobación del responsable, la imagen se cambió a **`node:22-alpine`**, porque Node 20 terminó su soporte en abril de 2026. Con Node 22 (22.23.5), `npm ci`, `npm run build` y `npm audit` (0 vulnerabilidades) pasan sin avisos de engine; plugin-react 5 exige `>=22.12.0`.

### Ruta del build en el `Dockerfile`

Error previo: la segunda etapa copiaba `COPY --from=web /web/dist /srv/frontend/dist`, pero `vite.config.ts` compila en `../backend/static` (en la etapa `web`, `/backend/static`). Como `/web/dist` no existe, `docker build` fallaba en ese paso. Además, FastAPI sirve `static/` desde `/srv/backend`, no desde `/srv/frontend/dist`.

- `Dockerfile`: ahora `COPY --from=web /backend/static ./static`, después de `COPY backend/ ./`, para que el sitio recién compilado sustituya la copia versionada.
- `README-ENTORNO.md`: decía que el build genera `frontend/dist`; ahora indica `backend/static/`.
- `vite.config.ts` no cambió, porque Render depende de `backend/static/`.

Verificación: `docker build` completo. Solo para esta prueba se usó una copia del Dockerfile que añade el certificado del proxy del entorno de verificación; el Dockerfile del repositorio no lo lleva. `npm ci` y `npm run build` corrieron en `node:22-alpine`, y la imagen final contiene los mismos `index-G1M1fVdK.js` e `index-BsvzXWJM.css` que `backend/static/`. Con el contenedor en marcha (SQLite), `/`, `/login`, `/privacidad`, `/app/customers`, `/health` y el JS enlazado desde `index.html` respondieron 200.

## 2026-11-25 — Precisión de precios en CSV y registro público en Docker

**Precios con tres decimales.** Si un producto tiene un precio numérico de `12.345`, el panel lo exporta como `12,345`. Al reimportar ese texto, el panel lo interpreta como `12345`. La API aplica la misma convención a los precios enviados como texto. El caso es ambiguo porque un único separador seguido de tres cifras también representa miles. Se comprobó que el importador convierte tanto `12,345` como `12.345` en `12345`, mientras que `1.250,75` se convierte en `1250.75`. Si se admiten precios con tres decimales, queda por definir un formato que conserve ese valor en la exportación y posterior importación. [Informe del 23 de noviembre](https://github.com/miguelate908/aura--intelligence/blob/5ba973fa28a0e14f4391b1107e3f431a19d44b20/docs/supervision/2026-11-23.md)

**Registro público en Docker.** El servicio `app` de `docker-compose.prod.yml` carga `.env.production`. Al resolver la configuración con `docker compose config` sobre una copia de `.env.production.example`, el entorno de la aplicación omitió `REGISTRATION_ENABLED`. En esas condiciones el backend habilita el registro público por defecto. Al añadir `REGISTRATION_ENABLED=false` a la copia, Compose pasó el valor al servicio y la función de configuración del backend devolvió `false`. El registro desactivado hace que `POST /auth/register` responda con HTTP 403.

Para un despliegue Docker que requiera altas privadas, configura `REGISTRATION_ENABLED=false` en su `.env.production`, recrea el servicio `app` y comprueba mediante `GET /auth/config` que `registration_enabled` sea `false`. El archivo `render.yaml` ya declara ese valor para Render. La verificación se realizó con la plantilla del repositorio y el código del backend; el valor efectivo de cada instalación depende de su entorno. [Bitácora del 22 de noviembre](https://github.com/miguelate908/aura--intelligence/blob/8242900bfc463f4da26f04bbb5c5f45cad85f98b/docs/bitacora/2026-11-22.md)

## 2026-11-24 — CORE-001: Migración de seguridad JWT (python-jose → PyJWT)

**Rama:** `claude/jwt-migration-pyjwt-6401df` (independiente de `master`; sin fusión automática)

### Motivo

`pip-audit` sobre `backend/requirements-dev.txt` reportaba, tras actualizar el resto de dependencias,
tres registros con dos identificadores distintos:

| Paquete | Versión | Identificador | Origen |
|---|---|---|---|
| ecdsa | 0.19.2 | PYSEC-2026-1325 (2 registros) | dependencia transitiva de python-jose |
| python-jose | 3.5.0 | PYSEC-2026-4298 | dependencia directa |

Ninguno tiene versión corregida publicada, por lo que la solución es retirar python-jose (y con él ecdsa).

### Inventario de uso de python-jose

Solo dos archivos lo importaban:

- `backend/core/security.py` — `from jose import JWTError, jwt` (validación de tokens).
- `backend/routers/auth.py` — `from jose import jwt` (emisión del token en `/auth/login`).

Ningún otro módulo importa `jose`, `ecdsa`, `rsa` ni `pyasn1`. `pip show` confirma que
`ecdsa`, `rsa` y `pyasn1` solo eran requeridos por python-jose, y `six` solo por ecdsa.

### Cambios

- `backend/requirements.txt`: `python-jose[cryptography]` → `PyJWT>=2.15.1,<3`
  (2.15.1 es la versión instalada y auditada sin vulnerabilidades conocidas).
- `backend/core/security.py`:
  - `import jwt` (PyJWT); `JWTError` → `jwt.InvalidTokenError` (base de expirado, firma inválida, mal formado y claim ausente).
  - `jwt.decode(..., algorithms=["HS256"], options={"require": ["sub", "exp"]})`: el token se rechaza si falta `sub` o `exp`.
    Antes, con python-jose, un token firmado sin `exp` se aceptaba indefinidamente.
  - `sub` se lee con `payload["sub"]` y se convierte a entero; cualquier fallo → 401.
- `backend/routers/auth.py`: `from jose import jwt` → `import jwt`. La llamada `jwt.encode(...)` es compatible sin cambios.
- `backend/tests/test_jwt_tokens.py` (nuevo, 13 pruebas): emisión HS256 con expiración de 30 min, login válido/erróneo,
  rechazo de tokens expirados, sin `exp`, sin `sub`, `sub` no numérico, usuario inexistente, otra clave, otro algoritmo (HS512),
  `alg: none`, payload manipulado, token mal formado y ausencia de token.

Sin cambios en: algoritmo (HS256), expiración (30 min), forma de la respuesta de `/auth/login`
(`access_token`, `token_type`, `expires_in`), lógica de aislamiento por empresa (`company_id` del usuario en base de datos),
secreto JWT ni base de datos.

### Verificación (entornos virtuales aislados; no se tocó el `.venv` de la copia principal)

| Verificación | Resultado |
|---|---|
| Pruebas antes de migrar (python-jose) | 12 passed |
| Pruebas tras migrar | 25 passed (12 existentes + 13 nuevas) |
| Pruebas tras desinstalar python-jose, ecdsa, rsa, pyasn1, six | 25 passed |
| Instalación limpia desde `requirements-dev.txt` | solo PyJWT 2.15.1; sin jose/ecdsa/rsa/pyasn1 |
| `pip check` | No broken requirements found |
| `pip-audit` (entorno) | No known vulnerabilities found |
| `pip-audit -r backend/requirements.txt` | No known vulnerabilities found |
| Aislamiento entre empresas (`test_user_can_only_read_and_write_data_for_their_company`, `test_assistant_chat_...`) | passed |

Prueba manual con `uvicorn` local (SQLite temporal y secreto de prueba, no el de producción):
registro 200, login 200 con `expires_in` 1800, token válido 200, token inválido 401, token expirado 401,
sin token 401, contraseña incorrecta 401.

### Notas y pendientes

- El aviso de `setuptools 65.5.0` que aparece en entornos virtuales recién creados con Python 3.11.9 viene del propio
  `venv`, no de `requirements.txt`; se resuelve con `pip install --upgrade setuptools` en el entorno.
- Los tokens emitidos con python-jose siguen siendo válidos con PyJWT (mismo formato, HS256, `sub` como cadena, `exp`).
- El `.venv` local de la copia principal aún tiene python-jose 3.5.0 y ecdsa 0.19.2, porque `master` todavía los usa.
  Tras fusionar el PR: `pip uninstall python-jose ecdsa rsa pyasn1 six` y `pip install -r backend/requirements.txt`.
- No se avanzó a CORE-002.
