# AURA Intelligence — Kit de ventas

Materiales listos para usar con el plan de `PLAN-COMERCIAL.md`. Reemplaza lo que está entre `[corchetes]`.

---

## 0. Mensaje base: complemento de Siigo y Alegra

Úsalo como idea central en todos los mensajes, demos y propuestas (ver `PLAN-COMERCIAL.md` §3.1):

> **"Siigo o Alegra llevan tu contabilidad. AURA ordena y conecta lo que hoy vive en Excel: tus clientes, tus productos y tus bodegas. Nosotros cargamos los archivos; tú no cambias de sistema."**

- Di siempre "complementa", nunca "reemplaza" ni "se integra con" (la integración no existe).
- Si el prospecto no usa Siigo ni Alegra, nombra el software que use o di "tu software contable".

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

### Contadores y consultores (canal de referidos del 20 %)

Un contador es un **prospecto de alianza**, no un cliente ni un socio, hasta que acepte por escrito las condiciones de referidos. El mensaje debe dejar claro que AURA no toca su trabajo ni el software contable de sus clientes.

**Primer mensaje (WhatsApp, correo o LinkedIn):**
> Hola [nombre]. Sé que atiendes a varias pymes, seguramente con Siigo o Alegra. No te vengo a ofrecer otro programa contable: AURA complementa ese software. Ellos siguen llevando la contabilidad contigo; nosotros ordenamos y conectamos lo que hoy tienen en Excel —clientes, productos y bodegas— y les entregamos un informe de calidad de esos datos. Eso también te ahorra a ti pedir y corregir archivos cada mes. Por cada cliente que recomiendes y contrate, te reconozco el 20 % de lo que pague el primer año. ¿Te muestro en 20 minutos cómo funciona?

**Si responde "mis clientes ya tienen Siigo/Alegra":**
> Justo por eso. No cambian nada de lo que ya usan contigo. Lo que ordenamos es la parte operativa que no está en el contable, o que está repetida en varios Excel: listas de clientes, catálogos de productos, un archivo por bodega. Si el software les permite exportar a Excel, cargamos ese archivo también.

**Si pregunta cuánto gana:**
> El 20 % de lo que el cliente pague por su plan el primer año; el piloto inicial no cuenta. Por ejemplo, un cliente en el Plan Profesional mensual paga COP 8.280.000 el primer año; tu parte serían COP 1.656.000. En el Esencial mensual serían COP 696.000. Te pago tu parte en los 30 días siguientes a cada pago que hace el cliente, y si el cliente no paga no hay comisión. Te lo dejo por escrito antes de que me presentes a nadie.

*(Cálculo: 20 % × mensualidad × 12. Si el cliente paga anual —10 mensualidades— la base es menor: COP 1.380.000 en Profesional y COP 580.000 en Esencial. Condiciones aprobadas el 25-11-2026 en `PLAN-COMERCIAL.md` §6: el Piloto no cuenta para la comisión, y cada pago al contador se hace en los 30 días siguientes a cada pago recibido del cliente.)*

**Cierre de la conversación con el contador:** pide que te presente a **una** pyme concreta que viva el problema, no una lista. Registra al contador en la hoja de oportunidades con canal `referido-contador`.

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
| "¿Por qué pago más que por Siigo / Alegra?" | "Porque no es lo mismo y no lo reemplaza. Su Siigo o Alegra hace su contabilidad y su facturación, y lo debe seguir usando. Con AURA paga que alguien cargue, depure y mantenga ordenados sus clientes, productos y bodegas que hoy están en Excel: en el Esencial hacemos nosotros una recarga cada mes. La comparación justa no es contra otro programa, sino contra las horas que su equipo pasa juntando archivos. ¿Cuántas son a la semana?" *Luego haz la cuenta en voz alta: horas al mes × [valor hora] frente a COP 290.000. Si la cuenta no da, no insistas: ofrece el Piloto como prueba acotada o descalifica.* |
| "Ya tenemos Excel." | "Exacto, y lo seguirán usando si quieren. AURA no reemplaza su Excel: lo conecta, para que dejen de buscar en siete archivos." |
| "Ya tenemos un software contable / ERP." | "Ese software lleva la contabilidad; AURA da la visión operativa de clientes, productos y bodegas que normalmente queda fuera. No hay que cambiar nada de lo que ya usan." |
| "Siigo / Alegra ya maneja inventario y bodegas." | "Si su equipo ya lleva ahí clientes, productos y bodegas al día, probablemente no nos necesita para eso, y se lo digo con franqueza. ¿Hoy todo está ahí, o todavía hay archivos de Excel aparte?" *Si todo está en el contable, agradece y descalifica. AURA no maneja cantidades de inventario: no lo prometas.* |
| "¿Se conecta con mi Siigo / Alegra?" | "Hoy no hay una conexión automática. Si su software le deja exportar a Excel o CSV, cargamos ese archivo; lo probamos con un archivo suyo antes de proponerle nada." |
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

---

## 8. Borrador de acuerdo de referidos (contadores y consultores)

> **Borrador para revisión.** No es asesoría legal ni tributaria. Hazlo revisar por tu contador o abogado antes de firmar el primero (ver `PLAN-COMERCIAL.md` §5). Las condiciones de comisión son las aprobadas el 25-11-2026 (`PLAN-COMERCIAL.md` §6); la vigencia del registro (90 días), la duración (un año) y el preaviso (30 días) también quedaron aprobados ese día. Lo que está entre `[corchetes]` debes completarlo o decidirlo; las cifras marcadas como *sugerido* no están aprobadas.

> **ACUERDO DE REFERIDOS — AURA INTELLIGENCE**
>
> Entre **[tu nombre completo o razón social]**, identificado con [C.C./NIT] [número], en adelante **AURA**, y **[nombre del contador o consultor]**, identificado con [C.C./NIT] [número], en adelante **EL REFERIDOR**, se celebra este acuerdo el [fecha], en [ciudad].
>
> **1. Objeto.** EL REFERIDOR podrá presentar a AURA empresas interesadas en sus servicios. AURA pagará una comisión por cada empresa referida que contrate y pague un plan, en los términos de este acuerdo.
>
> **2. Cómo se registra un referido.** El referido existe solo cuando EL REFERIDOR envía a AURA, por escrito (correo o WhatsApp), el nombre de la empresa y de la persona de contacto, y AURA confirma por escrito que esa empresa no estaba ya en su registro de oportunidades. Si la empresa ya estaba registrada, no se genera comisión. El registro vale por **noventa (90) días**: si en ese plazo la empresa no contrata un plan, el referido vence. EL REFERIDOR puede volver a registrarlo después.
>
> **3. Comisión.** AURA pagará a EL REFERIDOR el **veinte por ciento (20 %)** de los valores efectivamente pagados por la empresa referida por su **Plan Esencial o Plan Profesional**, mensual o anual, durante los **doce (12) primeros meses** contados desde el inicio de ese plan. La base de cálculo excluye el IVA [*confirmar con tu contador*].
>
> **4. Pagos que no generan comisión.** No generan comisión: (a) el **Piloto AURA 30 días**, incluido el valor del Piloto que se acredite al plan anual; (b) los desarrollos a medida; (c) los pagos recibidos después de los doce primeros meses; (d) los valores que AURA devuelva o no logre cobrar.
>
> **5. Forma y plazo de pago.** AURA pagará la comisión dentro de los **treinta (30) días calendario siguientes a cada pago efectivamente recibido** de la empresa referida, mediante transferencia a la cuenta que indique EL REFERIDOR. Si la empresa no paga, se atrasa o cancela, no se causa comisión por los períodos no pagados. Si la empresa paga un año por adelantado, la comisión se calcula sobre ese pago y se paga en el mismo plazo.
>
> **6. Documentos y tributos.** Para cada pago, EL REFERIDOR entregará a AURA factura electrónica o documento soporte / cuenta de cobro, según su régimen tributario. AURA aplicará las retenciones que exija la ley. Cada parte responde por sus propios impuestos. [*Confirmar con tu contador qué documento y qué retenciones aplican.*]
>
> **7. Independencia.** EL REFERIDOR actúa de forma independiente. Este acuerdo no crea relación laboral, sociedad, agencia comercial ni representación. EL REFERIDOR no puede firmar contratos, fijar precios, ofrecer descuentos ni recibir pagos a nombre de AURA.
>
> **8. Qué puede y qué no puede decir EL REFERIDOR.** Puede describir AURA como un servicio y una herramienta que ordena y conecta clientes, productos y bodegas, como complemento del software contable de la empresa. **No puede** afirmar que AURA se integra con Siigo, Alegra u otro software, que maneja inventario con cantidades, que usa inteligencia artificial, ni ofrecer funciones o precios distintos a los publicados por AURA. AURA le entregará el material de presentación vigente.
>
> **9. Datos personales y confidencialidad.** Cada parte trata los datos personales que reciba conforme a la Ley 1581 de 2012 y sus normas reglamentarias. EL REFERIDOR solo compartirá datos de contacto de personas que hayan aceptado ser contactadas por AURA. AURA no compartirá con EL REFERIDOR la información de negocio de la empresa referida (clientes, productos, bodegas, precios) sin autorización escrita de esa empresa. Ambas partes mantendrán confidencial la información de la otra parte que no sea pública.
>
> **10. No exclusividad.** Ninguna parte tiene exclusividad. EL REFERIDOR puede recomendar otros servicios y AURA puede tener otros referidores.
>
> **11. Duración y terminación.** Este acuerdo dura **un (1) año** y se renueva automáticamente por períodos iguales, salvo aviso escrito de cualquiera de las partes con **treinta (30) días** de anticipación. Si el acuerdo termina, AURA seguirá pagando la comisión de los referidos que ya hayan contratado un plan, hasta completar sus doce primeros meses.
>
> **12. Cambios.** Cualquier cambio en la comisión o en estas condiciones debe constar por escrito y firmado por ambas partes. Los cambios no afectan a los referidos que ya hayan contratado un plan.
>
> **13. Ley y controversias.** Se rige por la ley colombiana. Las partes intentarán resolver cualquier diferencia de forma directa durante [30 días — *sugerido*] antes de acudir a [la jurisdicción ordinaria / un centro de conciliación de [ciudad]].
>
> **Firmas.**
> AURA: [nombre], [C.C./NIT], firma, fecha.
> EL REFERIDOR: [nombre], [C.C./NIT], firma, fecha.

**Antes de enviarlo a un contador:**
1. Decide el único valor que sigue como *sugerido*: el plazo de arreglo directo de la cláusula 13 (30 días), y si las diferencias van a la jurisdicción ordinaria o a un centro de conciliación.
2. Confirma con tu contador si la comisión se calcula antes o después de IVA, qué documento te debe entregar el referidor y qué retenciones aplicas.
3. Registra cada contador en la hoja de oportunidades (§7) con canal `referido-contador` y estado `alianza propuesta` → `alianza firmada`. Hasta que firme, es un prospecto de alianza, no un socio.
