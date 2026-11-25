# AURA Intelligence — Kit de ventas

Materiales listos para usar con el plan de `PLAN-COMERCIAL.md`. Reemplaza lo que está entre `[corchetes]`.

---

## 1. Mensajes de primer contacto

### Red personal (WhatsApp o correo)
> Hola [nombre], ¿cómo vas? Estoy lanzando AURA, una herramienta para que las pymes tengan sus clientes, productos y bodegas organizados en un solo lugar, sin seguir peleando con archivos de Excel. Estoy buscando 5 empresas para un piloto con acompañamiento personal. ¿Conoces a algún gerente de una distribuidora, comercializadora o fábrica que viva ese problema? Me ayudaría muchísimo una presentación de 20 minutos.

### LinkedIn — secuencia de 3 mensajes
**Día 0 (con la solicitud de conexión):**
> Hola [nombre], trabajo con pymes de [sector] en [ciudad] ayudándoles a organizar la información de clientes, productos y bodegas. Me gustaría conectar.

**Día 2 (si acepta):**
> Gracias por conectar, [nombre]. Una pregunta rápida: en [empresa], ¿la información de clientes, productos y bodegas vive en un mismo sistema o en varios archivos? Estoy hablando con gerentes de operaciones para entender cómo lo manejan.

**Día 7 (si responde con un dolor):**
> Tiene mucho sentido. Eso es justo lo que resolvemos con AURA: cargamos sus archivos por ustedes y en 30 días tienen todo conectado y consultable. ¿Te parece si te lo muestro en 30 minutos esta semana? [enlace de agenda]

### Contadores y consultores
> Hola [nombre]. Sé que atiendes a varias pymes. Muchas tienen su información operativa dispersa en Excel, y eso también te complica el trabajo a ti. Estoy lanzando AURA para resolver eso, y ofrezco el 20 % del primer año por cada cliente que recomiendes y contrate. ¿Te puedo mostrar en 20 minutos de qué se trata?

---

## 2. Guion de descubrimiento (20 minutos)

Objetivo: confirmar dolor, presupuesto y quién decide. **No hagas la demo en esta llamada.**

1. **Contexto (3 min):** "Cuéntame brevemente qué hace [empresa] y cómo está organizado el equipo."
2. **Situación actual (5 min):**
   - ¿Dónde guardan hoy la información de clientes, productos y bodegas?
   - ¿Cuántos archivos o sistemas distintos usan? ¿Quién los actualiza?
   - ¿Cuántos clientes, productos y bodegas tienen, más o menos?
3. **Dolor (5 min):**
   - ¿Cuándo fue la última vez que no encontraron un dato a tiempo? ¿Qué pasó?
   - ¿Cuántas horas a la semana se dedican a consolidar archivos?
   - Si esto siguiera igual un año más, ¿qué les costaría?
4. **Decisión (4 min):**
   - Además de ti, ¿quién participa en decidir una herramienta como esta?
   - ¿Han intentado resolverlo antes? ¿Qué pasó?
   - ¿Hay un presupuesto aproximado para mejorar esto este trimestre?
5. **Siguiente paso (3 min):** "Con lo que me cuentas, creo que te puedo mostrar algo útil. ¿Agendamos 30 minutos el [día] con [quien decide]?"

**Descalifica (y agradece) si:** no hay dolor concreto, no tienen datos, buscan un ERP completo o exigen IA como requisito principal.

---

## 3. Guion de demostración (30 minutos)

Prepara antes: `python scripts/seed_demo.py` e inicia sesión con la cuenta de demostración.

1. **(2 min) Recordar su dolor** con sus propias palabras de la llamada de descubrimiento.
2. **(5 min) Resumen:** panel con los totales. "Así se vería [empresa] el día 30."
3. **(8 min) Clientes, productos y bodegas:** búsqueda, paginación. Muestra la **importación desde CSV**: "Ustedes no digitan nada; nosotros cargamos sus archivos."
4. **(7 min) Grafo:** "Aquí ven cómo se conecta todo." Es el momento visual de la demo.
5. **(5 min) Asistente:** pregunta "resumen de mi empresa", "productos con precio mayor a 100000", "busca [nombre]". Aclara que funciona con consultas predefinidas, no con IA generativa.
6. **(3 min) Cierre:** "¿Me envías un archivo de muestra de clientes o productos? Con eso te preparo la propuesta del piloto en 24 horas."

Muestra la sección "Estado del producto" si preguntan por algo que no existe. Nunca digas "eso ya casi está".

---

## 4. Plantilla de propuesta de piloto

> **Propuesta de piloto AURA Intelligence para [Empresa]**
> Fecha: [fecha] · Válida por 15 días
>
> **Situación actual.** [2–3 frases con lo que dijeron en el descubrimiento: archivos, horas perdidas, consecuencias.]
>
> **Objetivo del piloto.** En 30 días, tener los clientes, productos y bodegas de [Empresa] centralizados y conectados en AURA, y entregar un informe de hallazgos sobre la calidad y organización de sus datos.
>
> **Alcance.**
> - Carga inicial desde Excel/CSV de hasta 5.000 registros.
> - Configuración de la cuenta de [Empresa].
> - Dos sesiones de trabajo: arranque (semana 1) y revisión de resultados (semana 4).
> - Informe de hallazgos: duplicados, campos incompletos, relaciones detectadas y recomendaciones.
>
> **Fuera del alcance.** Integraciones con otros sistemas, inventario con cantidades, varios usuarios por empresa, funciones de inteligencia artificial.
>
> **Inversión.** COP 1.200.000 + IVA si aplica, pago anticipado. El 100 % se descuenta del primer año si [Empresa] contrata un plan anual dentro de los 15 días siguientes al cierre del piloto.
>
> **Cronograma.**
> | Semana | Actividad |
> |---|---|
> | 1 | Sesión de arranque y entrega de archivos |
> | 2 | Carga y depuración de datos |
> | 3 | Uso por el equipo de [Empresa], ajustes |
> | 4 | Informe de hallazgos y reunión de cierre |
>
> **Datos personales.** [Empresa] es responsable del tratamiento de los datos que entrega; AURA actúa como encargado y los usa únicamente para prestar el servicio, según el acuerdo de tratamiento de datos anexo.
>
> **Aceptación.** Nombre, cargo, fecha y firma.

---

## 5. Respuestas a objeciones

| Objeción | Respuesta |
|---|---|
| "Es muy caro." | "¿Cuántas horas a la semana dedican hoy a consolidar archivos? A [valor hora], el Plan Profesional se paga con [X] horas al mes. Además, el piloto se descuenta si continúan." |
| "Ya tenemos Excel." | "Exacto, y lo seguirán usando si quieren. AURA no reemplaza su Excel: lo conecta, para que dejen de buscar en siete archivos." |
| "Ya tenemos un software contable / ERP." | "Ese software lleva la contabilidad; AURA da la visión operativa de clientes, productos y bodegas que normalmente queda fuera. No hay que cambiar nada de lo que ya usan." |
| "¿Tiene inteligencia artificial?" | "Hoy tiene un asistente de consultas con reglas, que responde preguntas frecuentes al instante. La IA está en la hoja de ruta, y los clientes del piloto deciden qué se construye primero." |
| "¿Y si después me quiero ir?" | "Sus datos son suyos. Al terminar les entregamos todo en Excel." *(Mientras no exista la exportación en el panel, hazla manualmente desde la base de datos.)* |
| "¿Es seguro?" | "Cada empresa solo ve sus propios datos, el acceso exige contraseña de 12 caracteres y la sesión caduca a los 30 minutos. No declaramos certificaciones que no tenemos." |
| "Déjame pensarlo." | "Claro. ¿Qué necesitarías ver para decidir? ¿Agendamos 15 minutos el [día] para resolverlo con [quien decide]?" |

---

## 6. Correo de cierre del piloto

> Asunto: Resultados del piloto AURA — [Empresa]
>
> Hola [nombre],
>
> En estos 30 días cargamos [N] clientes, [N] productos y [N] bodegas, detectamos [N] registros duplicados y [N] relaciones entre clientes y productos que antes no eran visibles. Adjunto el informe completo.
>
> Para seguir, propongo el Plan [Profesional] anual: COP [10 × mensualidad] (dos meses gratis), del cual descontamos los COP 1.200.000 del piloto. ¿Te parece si lo revisamos el [día] a las [hora]?
>
> Gracias por la confianza,
> [tu nombre]

---

## 7. Registro de oportunidades

Columnas mínimas para tu hoja o CRM: fecha · empresa · contacto · cargo · canal · sector · tamaño · dolor principal · estado · próximo paso · fecha del próximo paso · valor estimado.

Estados: `nuevo → contactado → descubrimiento → demo → propuesta → piloto → cliente` / `perdido (motivo)`.

Revisa la hoja cada lunes: ninguna oportunidad activa debe quedar sin "próximo paso" con fecha.
