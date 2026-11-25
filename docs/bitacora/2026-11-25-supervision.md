## 2026-11-25 — Supervisión diaria + mejora DATA-001 (precios en formato colombiano en la importación)

**Rama:** `claude/laughing-curie-m34ua3` (sin fusionar; requiere tu revisión)

### A. Supervisión técnica

| Verificación | Resultado |
|---|---|
| Estado del repositorio | `master` en `f70e4f5` (PR #14, CORE-001 PyJWT fusionado). Árbol limpio. |
| Pruebas backend (pytest, SQLite) | 25 passed antes del cambio → 27 passed después |
| `pip-audit` sobre `requirements-dev.txt` | Sin vulnerabilidades conocidas (CORE-001 resuelto) |
| Frontend `npm ci` + `npm run build` (tsc + vite) | Compila sin errores |
| PostgreSQL 16 local (base temporal, no producción) | Arranque de la app, creación de las 9 tablas, registro/login, alta de cliente/producto/bodega, importación CSV, consultas, asistente, eventos: todo OK |
| Aislamiento entre empresas sobre PostgreSQL | Empresa B ve 0 clientes de A; consulta cruzada → 403; sin token → 401 |

**Advertencias y riesgos (sin corregir; requieren tu decisión):**

1. `npm audit`: 4 avisos (1 alto, 3 moderados).
   - `vite 5.4.21` / `esbuild` (alto/moderado): afectan **solo al servidor de desarrollo** (`npm run dev`), no al sitio publicado,
     que FastAPI sirve ya compilado. Mitigación hoy: no exponer `npm run dev` en redes públicas. Corrección: subir a Vite 6.4.4+ / 8.x (cambio mayor).
   - `react-router-dom 6.30.6` (moderado, redirección abierta y SSR): el código no navega a rutas controladas por el usuario ni usa SSR,
     así que la exposición real es baja. Corrección: React Router 7 (cambio mayor). Propuesta: hacerlo en una rama aparte con pruebas manuales del panel.
2. `backend/static/` (sitio compilado que usa Render) se versiona en git. Al recompilar hoy cambia el hash del bundle aunque el contenido
   es equivalente (mismos correos y textos). Riesgo: si alguien cambia `frontend/src` y olvida recompilar, producción queda desactualizada.
   Propuesta: que Render compile el frontend en el `buildCommand`. No se tocó.
3. Aviso de PyJWT en pruebas (`InsecureKeyLengthWarning`) solo en la prueba que firma con HS512 a propósito; no afecta producción (HS256).
4. Starlette avisa que `TestClient` con `httpx` está obsoleto; solo afecta a pruebas. Fijar versiones antes de que se retire.

### B. Mejora del día — DATA-001

- **Objetivo:** que un precio escrito como texto en formato colombiano (`150.000`, `$ 1.250,75`) se guarde con su valor real en cualquier importación por API.
- **Justificación:** el panel ya convertía bien los precios (`toNumber` en `Resource.tsx`), pero el backend usaba
  `replace(",", ".")`: `"150.000"` se guardaba como **150** y `"1.500,5"` se rechazaba. Cualquier cliente futuro de la API
  (scripts de carga de pilotos, integraciones con Siigo/Alegra) habría corrompido precios en silencio. Es gestión de datos del ICP colombiano.
- **Cambio:** `backend/routers/imports.py` → `normalize_price()`, misma regla que el panel (miles con punto o con coma, `$` y espacios ignorados).
- **Criterio de aceptación:** `"150.000"` → 150000, `"$ 1.250,75"` → 1250.75, `"1,250.75"` → 1250.75, `"29,5"` → 29.5; pruebas existentes intactas.
  ✅ Verificado con 2 pruebas nuevas y sobre PostgreSQL (`$ 150.000` guardado como 150000).
- **Limitación conocida:** `"1.500"` se interpreta como mil quinientos (convención colombiana), igual que en el panel.

### C–E. Comercial, monetización y marketing (investigación; nada enviado ni publicado)

- **Hallazgo de competencia:** Siigo (>1,2 M clientes en la región) y Alegra dominan contabilidad/facturación pyme; fuentes públicas ubican
  sus planes pyme entre ≈ COP 89.000 y 191.000/mes. El **Plan Esencial de AURA (COP 290.000)** cuesta más que un software contable completo.
  Riesgo de objeción "¿por qué pago más que por Siigo?". Recomendación: posicionar AURA como **complemento** ("tu Siigo/Alegra lleva la contabilidad;
  AURA ordena y conecta clientes, productos y bodegas que hoy viven en Excel") y vender primero el **Piloto** (servicio), no la suscripción.
- **Oportunidad de alianza (prospectos, no clientes):** contadores que ya atienden pymes con Siigo/Alegra; reportes del sector indican alto uso de IA
  entre contadores colombianos. Encaja con el canal de referidos del 20 % del plan comercial.
- **Integración con más valor futuro:** importar clientes/productos exportados de Siigo/Alegra (CSV). Hoy no existe; no prometer. DATA-001 es un paso previo.
- **Acción comercial del día (para ti):** escribir a 3 contadores de tu red con el mensaje de `KIT-VENTAS.md §1 "Contadores y consultores"`, añadiendo:
  *"No reemplaza el Siigo o Alegra de tus clientes: ordena lo que hoy tienen en Excel y te deja un informe de calidad de datos"*.
- **Clientes confirmados:** ninguno registrado. **Ingresos recibidos:** COP 0 registrados.

### F. Control financiero

Sin gastos nuevos hoy. Esta sesión no realizó compras, suscripciones ni pagos. Costos fijos estimados del plan (no verificados con facturas):
Render starter + PostgreSQL basic-256mb, dominio y correo. Pendiente: que registres los costos reales para llevar el control.
