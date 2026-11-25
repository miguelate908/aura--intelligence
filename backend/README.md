# EDITH Intelligence API

API REST con FastAPI, SQLAlchemy y PostgreSQL. La documentación interactiva se publica en `/docs`.

## Inicio en Windows

Desde PowerShell, en esta carpeta:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` con una clave JWT aleatoria de al menos 32 caracteres. Si no tienes una instancia PostgreSQL local, inicia la alternativa Docker desde la raíz del proyecto:

```powershell
docker compose --env-file backend/.env -f docker-compose.yml/docker-compose.yml up -d
```

El archivo Compose usa `DB_NAME`, `DB_USER` y `DB_PASSWORD`; deben coincidir con los datos de conexión de `DATABASE_URL`. No inicies el contenedor si ya tienes otro PostgreSQL ocupando el puerto configurado. Después inicia la API desde la carpeta `backend`:

```powershell
uvicorn main:app --reload
```

Abre `http://127.0.0.1:8000/docs`. PostgreSQL debe estar iniciado y la base definida en `DATABASE_URL` debe existir.

## Flujo de autenticación

1. Registra al usuario administrador de una empresa con `POST /auth/register`, enviando `company_name`, `name`, `email` y `password`. La empresa y el usuario se crean juntos.
2. Inicia sesión con `POST /auth/login` enviando JSON con `email` y `password`.
3. Copia `access_token` y autoriza las rutas protegidas usando `Bearer <token>`.

Los usuarios solo pueden consultar o modificar datos de su empresa. Las rutas de datos devuelven `401` sin un token válido y `403` cuando se intenta usar otra empresa.

## Pruebas de autenticación y empresas

Instala las dependencias de desarrollo y ejecuta las pruebas. Estas usan SQLite temporal, así que no necesitan iniciar PostgreSQL:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Importación masiva (CSV)

Cada página del panel (Clientes, Productos, Bodegas) tiene **Importar desde CSV**. Acepta separador `,` o `;` (Excel en español) y encabezados con el nombre del campo o la etiqueta en pantalla (`Nombre`, `Correo`, `SKU`, `Precio`, `Ubicación`…). Los precios pueden venir como `29.500` o `1.250,75`. "Descargar plantilla" genera el archivo vacío con las columnas.

La importación es todo o nada: si una fila tiene errores (campo obligatorio vacío, SKU repetido o ya existente), no se guarda ninguna y el panel lista las filas a corregir. El límite es de 5.000 filas por archivo. API: `POST /import/{customers|products|warehouses}` con `{"rows": [...]}`.

## Exportación (CSV para Excel)

En Clientes, Productos y Bodegas, **Exportar CSV** descarga todos los registros que coinciden con la búsqueda, incluidas las demás páginas, con los mismos encabezados que acepta la importación, separador `;`, BOM UTF-8 y decimales con coma, para que Excel en español lo abra sin pasos extra. El archivo usa el formato de importación y se aplican las mismas validaciones, incluida la de SKU duplicado. Los valores que empiezan por `=`, `@`, `+` o `-` se neutralizan con un apóstrofo para evitar inyección de fórmulas en Excel (los teléfonos como `+57 300 1234567` y los números negativos se dejan igual). La exportación ocurre en el navegador; no hay ruta nueva en la API.

## Empresa de demostración para ventas

```powershell
python scripts/seed_demo.py
```

Crea "Distribuidora Andina Demo" con 20 clientes, 20 productos, 3 bodegas y sus relaciones, e imprime el correo y una contraseña aleatoria. Volver a ejecutarlo borra y recrea solo esa empresa. Úsalo en una base de demostración, no en la de clientes.

## Plan comercial

La estrategia de precios, el proceso de venta y el kit de ventas están en `docs/comercial/`.
