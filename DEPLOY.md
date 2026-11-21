# Publicar EDITH Intelligence en internet

## Qué necesitas
1. Un servidor con **Docker** (un VPS Linux de cualquier proveedor) y su dirección IP pública.
2. Un **dominio**, con un registro DNS tipo **A** que apunte a esa IP.
3. Los puertos **80 y 443** abiertos en el servidor.

## Pasos
1. Copia el proyecto al servidor (con `git clone` o `scp`). No copies `.env` ni `.venv`.
2. Crea el archivo de configuración:
   ```bash
   cp .env.production.example .env.production
   nano .env.production
   ```
   Cambia **todos** los valores. Para generar claves aleatorias:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(48))"
   ```
   Usa una distinta para `DB_PASSWORD`, `JWT_SECRET_KEY` y `ADMIN_API_KEY`.
3. Arranca todo:
   ```bash
   docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build
   ```
   Caddy obtiene el certificado HTTPS solo, la primera vez puede tardar un minuto.
4. Abre `https://tu-dominio.com`. Revisa el estado con:
   ```bash
   docker compose -f docker-compose.prod.yml ps
   docker compose -f docker-compose.prod.yml logs -f app
   ```

## Contactos que llegan
- Si configuraste `SMTP_*` y `LEADS_NOTIFY_TO`, recibes un correo por cada contacto.
- Siempre puedes consultarlos en `GET /contact/leads` con el encabezado `X-Admin-Key: <ADMIN_API_KEY>`.

## Mantenimiento
- **Actualizar**: sube los cambios y repite el comando del paso 3.
- **Copia de seguridad de la base** (hazla a menudo):
  ```bash
  docker compose -f docker-compose.prod.yml exec db pg_dump -U aura_user aura_db > respaldo.sql
  ```

## Antes de abrirlo al público
- [ ] Quitar `contact.py` del `.gitignore` (si no, ese archivo no se sube a Git).
- [ ] Revisar con un profesional legal la política de privacidad.
- [ ] Probar el formulario de contacto y el registro desde otro dispositivo.
- [ ] Confirmar que `.env.production` no está en Git.
