# Pipeline de Extracción: Apify en Cloud Run

Este diseño modular permite ejecutar scrapers de Apify de forma escalable y sin servidor, integrando los resultados directamente en el Grafo de Grafos.

## 1. Arquitectura del Pipeline
1. **Trigger:** Cloud Scheduler o Webhook HTTP.
2. **Compute:** Cloud Run (Docker Container).
3. **Action:** Lanza el Actor de Apify (ej: `instagram-comment-scraper`).
4. **Storage:** Escribe el JSON crudo en Google Cloud Storage (GCS).
5. **Cratization:** Un script posterior convierte el JSON en un "Data Crate" para el análisis.

## 2. Dockerfile Sugerido (Cloud Run)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Variables de Entorno (Inyectadas por Secret Manager)
ENV APIFY_TOKEN=""
ENV GCS_BUCKET=""

CMD ["python", "main_cloudrun.py"]
```

## 3. Registro como Crate de Infraestructura
- **ID:** `saiel.infra_apify_bridge`
- **Misión:** Orquestar la extracción y asegurar la persistencia en el Data Lake.
