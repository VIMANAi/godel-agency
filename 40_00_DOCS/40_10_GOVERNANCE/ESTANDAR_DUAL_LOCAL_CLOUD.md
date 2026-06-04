# SAIEL: ESTÁNDAR DE PROCESAMIENTO DUAL (LOCAL & CLOUD)

El sistema SAIEL implementa una arquitectura modular de "Proveedores de Inteligencia" para adaptarse a diferentes escenarios electorales.

---

## 🔒 OPCIÓN 1: PROCESAMIENTO 100% LOCAL (MODO BÚNKER)
*Ideal para: Máxima privacidad, cumplimiento estricto de LGPDPPSO y operación sin dependencia de internet.*

- **Estructura:** `engine/providers/local/`
- **Motor:** Ollama + DeepSeek-R1 (7b/14b).
- **Metodología:**
  1. Ingesta de datos vía `data_ingestion.py`.
  2. Inferencia en GPU/CPU local para análisis de sentimiento.
  3. Almacenamiento en archivos locales (NDJSON/SQLite).
- **Estándar:** Ningún dato debe salir de la red local. El anonimizador es opcional pero recomendado.

## ☁️ OPCIÓN 2: CLOUD-NATIVE (MODO ESCALABILIDAD)
*Ideal para: Grandes volúmenes de datos nacionales y despliegues rápidos.*

- **Estructura:** `engine/providers/cloud/`
- **Motor:** Vertex AI (Gemini 1.5 Flash) + BigQuery.
- **Metodología:**
  1. Los datos se suben a un Bucket de GCS (Google Cloud Storage).
  2. **Mandato Obligatorio:** Anonimización PII vía `saiel.data_anonymizer` antes de la subida.
  3. Inferencia masiva paralela en Vertex AI.
- **Estándar:** Auditoría de costos activa y cumplimiento de GDPR/Google Cloud Compliance.

---

## 🚦 MECANISMO DE CONMUTACIÓN (THE SWITCH)
La selección del motor se realiza mediante la variable de entorno `SAIEL_ENGINE_MODE` (`local` | `cloud`).

### Ejemplo de Uso en Sandbox:
```python
from engine.providers.local import SentimentProvider as LocalSenti
from engine.providers.cloud import SentimentProvider as CloudSenti

# El orquestador selecciona automáticamente según configuración
```

---
*Gobernanza Técnica SAIEL - Ingeniería Senior*
