# AURA Intelligence API

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
