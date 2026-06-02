# Dockerfile para SAIEL Apify Extractor en Cloud Run
FROM python:3.11-slim

# Evitar la generación de archivos .pyc y permitir logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Instalación de dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalación de dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir apify-client google-cloud-storage functions-framework

# Copiar el código del proyecto
COPY main_cloudrun.py .

# Puerto por defecto para Cloud Run
EXPOSE 8080

# Ejecutar el orquestador
CMD ["functions-framework", "--target=orchestrate_extraction", "--port=8080"]
