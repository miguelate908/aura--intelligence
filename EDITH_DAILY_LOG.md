# EDITH — Registro diario

## 2026-11-25 — Posicionamiento frente a Siigo/Alegra y propuesta sobre el Plan Esencial

**Rama:** `claude/determined-hamilton-ljygsk`, creada desde `master` (`559e1f5`). Está sin fusionar y requiere tu revisión. No se envió ni se publicó nada.

**Origen.** Es la sección C–E de la investigación comercial del 25 de noviembre. Esa sección está en la rama `claude/laughing-curie-m34ua3`, que no se ha fusionado en `master`, y por eso no aparece en este archivo. Allí se detectó que el Plan Esencial (COP 290.000/mes) cuesta más que los planes pyme de Siigo y Alegra, lo que facilita la objeción "¿por qué pago más que por Siigo?".

**Verificación de precios (25-11-2026).**

- Las páginas oficiales de Siigo `siigo.com/planes/`, `/precios/` y `/planes-precios/` devolvieron HTTP 404. Las de Alegra `alegra.com/colombia/precios/` y `/contabilidad/precios/` cargaron, pero no mostraban planes. No se pudo confirmar ningún precio con el proveedor.
- Hay dos fuentes de terceros que coinciden entre sí: blog.alegra.com/colombia/alegra-vs-siigo-colombia/, actualizada el 16-07-2026, y guiadesoftware.com/blog/mejor-software-contabilidad-colombia, actualizada el 11-11-2026.
  - Siigo Nube Profesional: COP 145.993/mes con pago anual.
  - Siigo Nube Emprendedor: COP 191.327/mes con 3 usuarios, y COP 2.869.900/año a precio de lista.
  - Alegra: Emprendedor COP 74.900, Pyme COP 163.900, Pro COP 250.900 y Plus COP 319.900 al mes. Con pago anual hay un 25 % menos.
  - Ninguna de las dos fuentes indica el IVA.
- El rango anterior, COP 89.000–191.000, no recoge los extremos. El plan de entrada de Alegra cuesta menos, y Alegra Pro y Plus cuestan lo mismo o más que el Esencial. Además, Alegra Pyme ya incluye 2 bodegas.

**Cambios propuestos.**

- `docs/comercial/PLAN-COMERCIAL.md`:
  - §2: indica que el ICP ya usa Siigo o Alegra.
  - §3.1 (nuevo): posicionamiento como complemento. Recoge lo que no se promete, como la integración, y cuándo descalificar.
  - §4.1 (nuevo): tabla de precios de referencia con su fuente y fecha, las opciones A, B y C, y una recomendación.
  - §6.3: los contadores figuran como prospectos de alianza.
- `docs/comercial/KIT-VENTAS.md`:
  - §0 (nuevo): mensaje base.
  - §1: nueva variante para contadores, con respuestas de seguimiento y el cálculo de la comisión del 20 %.
  - §5: tres objeciones nuevas: "¿por qué pago más que por Siigo/Alegra?", "Siigo/Alegra ya maneja inventario" y "¿se conecta con mi Siigo/Alegra?".

**Recomendación de precios: opción A, aprobada por ti el 25-11-2026; no cambia ningún precio.** La opción A consiste en mantener el Esencial en COP 290.000, ofrecerlo después del Piloto y del Profesional, y presentarlo como servicio mensual de datos ordenados que complementa el software contable.

- Hoy no hay datos de ventas que justifiquen bajarlo.
- El descuento de fundador congelaría de por vida un precio más bajo.
- Regla de revisión: si al menos 3 de las primeras 10 demos se pierden por precio frente a Siigo o Alegra, se evalúa un plan inferior sin servicio (opción C).

**Pendientes para ti.**

1. ~~Decidir entre A, B o C.~~ Hecho: opción A aprobada el 25-11-2026.
2. Definir por escrito si el Piloto cuenta para la comisión de referidos y en qué plazo se paga.
3. Revisar las cifras en las webs de Siigo y Alegra antes de citarlas a un prospecto.
4. La rama `claude/laughing-curie-leps3u` cambia la marca a "EDITH Intelligence". Este cambio conserva "AURA", igual que `master`. Si fusionas ambas, habrá que unificar el nombre en las secciones nuevas.

**Clientes confirmados:** ninguno. **Ingresos registrados:** COP 0. Los contadores mencionados son prospectos de alianza, no clientes.

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
