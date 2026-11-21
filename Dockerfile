# 1) Compila el sitio (React + Vite)
FROM node:20-alpine AS web
WORKDIR /web
COPY frontend/package*.json ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi
COPY frontend/ ./
RUN npm run build

# 2) API FastAPI + sitio compilado en un solo servidor
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1
WORKDIR /srv/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./
COPY --from=web /web/dist /srv/frontend/dist
RUN useradd -m app && chown -R app /srv
USER app
EXPOSE 8000
# --proxy-headers: toma la IP real del visitante que reenvía Caddy (para el límite de envíos)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips=*"]
