# Entorno de desarrollo EDITH

## Estructura
```
aura- intelligence\
├── .venv\            entorno virtual de Python
├── setup.ps1         prepara todo (una sola vez)
├── dev.ps1           arranca backend + frontend
├── backend\          FastAPI (tu proyecto actual)
└── frontend\         sitio web React + TypeScript + Vite
    └── src\ (api.ts, auth.tsx, App.tsx, pages\)
```

## Primera vez (PowerShell, en la carpeta raíz)
```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\setup.ps1
.\dev.ps1
```
Requisitos: Python 3.11 y Node.js LTS (https://nodejs.org).
Sitio: http://localhost:5173 · API y documentación: http://127.0.0.1:8000/docs

## Cómo funciona
El sitio llama a `/api/...`; Vite lo reenvía al backend en el puerto 8000, así que no hay problemas de CORS.

## Solicitudes de demostración
El formulario público guarda cada solicitud en la tabla `demo_requests` y envía una notificación a `DEMO_REQUEST_EMAIL` cuando SMTP está configurado en `backend/.env`. Define `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` y `SMTP_FROM`; para servidores que requieren TLS, conserva `SMTP_STARTTLS=true`. No compartas ni subas las credenciales SMTP.

El formulario limita cada IP a cinco envíos por diez minutos y usa un campo señuelo antispam. Este límite vive en memoria del proceso; en una instalación con varias instancias debe reemplazarse por un limitador compartido.

## Para crecer
- Cada módulo nuevo (inventario, pedidos, reportes) va en `frontend/src/pages/` y se registra en `App.tsx`.
- Cuando un módulo tenga lógica propia, agrúpalo en `src/features/<modulo>/`.
- Producción: `npm run build` genera `backend/static`, que FastAPI sirve. Render compila el sitio en cada despliegue (`docs/DESPLIEGUE.md`, sección 6).
